from enums import Connective, Type, Quantifier
from formula import Unary, Binary, Variable, Function, Formula


class ResolutionProver:
    def __init__(self, arg: [Formula]):
        self._arg = arg
        self._clauses = []
        self._support = []
        self._subscript = 0

    def print_argument(self):
        for formula in self._arg:
            quant_list = formula.get_quant_list()
            if len(quant_list) > 0:
                for item in quant_list:
                    if item[0] == Quantifier.EXISTENTIAL:
                        print("∃" + item[1], end="")
                    if item[0] == Quantifier.UNIVERSAL:
                        print("∀" + item[1], end="")
            formula.print_formula()
            print("")

    def print_clauses(self):
        pass

    def negate_conclusion(self):
        conclusion = self._arg.pop()
        unary = Unary(conclusion, Quantifier.NONE, True, "")
        unary.set_var_count(conclusion.get_var_count())
        self._arg.append(unary)

    def remove_arrows(self, formula: Formula) -> Formula:
        formula_type = formula.get_formula_type()
        if formula_type == Type.BINARY:
            new_left = self.remove_arrows(formula.get_left())
            new_right = self.remove_arrows(formula.get_right())

            if formula.get_connective() == Connective.IMPLICATION:
                formula.set_left(
                    Unary(new_left, Quantifier.NONE, True, "")
                )
                formula.set_right(new_right)
                formula.set_connective(Connective.OR)

            if formula.get_connective() == Connective.BICONDITIONAL:
                formula.set_left(
                    Binary(
                        new_left,
                        new_right,
                        Connective.AND
                    )
                )
                formula.set_right(
                    Binary(
                        Unary(new_left, Quantifier.NONE, True, ""),
                        Unary(new_right, Quantifier.NONE, True, ""),
                        Connective.AND
                    )
                )
                formula.set_connective(Connective.OR)

        if formula_type == Type.UNARY:
            formula.set_inside(
                self.remove_arrows(formula.get_inside())
            )
        return formula

    def move_negation_inward(self, formula: Formula, negation_outside: bool) -> Formula:
        formula_type = formula.get_formula_type()
        if formula_type == Type.BINARY:
            # recursively moving negation inwards for all parts of the formula
            formula.set_left(
                self.move_negation_inward(
                    formula.get_left(),
                    negation_outside
                )
            )
            formula.set_right(
                self.move_negation_inward(
                    formula.get_right(),
                    negation_outside
                )
            )
            # Perform procedure for De Morgan's Law
            if negation_outside and formula.get_connective() == Connective.AND:
                formula.set_connective(Connective.OR)
            elif negation_outside and formula.get_connective() == Connective.OR:
                formula.set_connective(Connective.AND)

        if formula_type == Type.UNARY:
            if negation_outside and formula.get_negation():
                # if previous negation cancels out, we don't reverse quantifiers no negation passed
                formula.set_inside(
                    self.move_negation_inward(formula.get_inside(), False)
                )
            elif negation_outside or formula.get_negation():
                # if previous negates results in a negation, we need to reverse quantifiers and pass the negation
                if formula.get_quantifier() == Quantifier.UNIVERSAL:
                    formula.set_quantifier(Quantifier.EXISTENTIAL)
                elif formula.get_quantifier() == Quantifier.EXISTENTIAL:
                    formula.set_quantifier(Quantifier.UNIVERSAL)

                formula.set_inside(
                    self.move_negation_inward(formula.get_inside(), True)
                )
            else:
                # if no negation, we don't reverse quantifiers no negation passed
                formula.set_inside(
                    self.move_negation_inward(formula.get_inside(), False)
                )

        if (negation_outside
                and formula_type != Type.BINARY
                and formula_type != Type.UNARY):
            # if formula is function, and there's a negation, wraps it in a unary with negation
            formula = Unary(formula, Quantifier.NONE, True, "")
        if formula_type == Type.UNARY:
            # if formula is unary, then we are returning to previous, don't add negation
            formula.set_negation(False)

        return formula

    def standardize_variables(self, formula: Formula, var_name: str) -> Formula:
        formula_type = formula.get_formula_type()
        if formula_type == Type.UNARY:
            if (formula.get_quant_var() == var_name
                    and formula.get_quantifier() != Quantifier.NONE):
                self._subscript += 1
                formula.set_quant_var(
                    var_name + str(self._subscript)
                )
            formula.set_inside(
                self.standardize_variables(formula.get_inside(), var_name)
            )
        elif formula_type == Type.BINARY:
            formula.set_left(
                self.standardize_variables(
                    formula.get_left(),
                    var_name
                )
            )
            formula.set_right(
                self.standardize_variables(
                    formula.get_right(),
                    var_name
                )
            )
        elif formula_type == Type.FUNCTION:
            if formula.get_inside().get_var_name() == var_name and self._subscript != 0:
                formula.set_var(var_name + str(self._subscript))
        else:
            if formula.get_var_name() == var_name:
                formula.set_var(var_name + str(self._subscript))
        return formula

    def move_quantifiers_to_front(self, formula: Formula, quant_list: []) -> Formula:
        formula_type = formula.get_formula_type()
        if formula_type == Type.BINARY:
            quant_list = self.move_quantifiers_to_front(
                formula.get_left(),
                quant_list
            )
            quant_list = self.move_quantifiers_to_front(
                formula.get_right(),
                quant_list
            )
        elif formula_type == Type.UNARY:
            if formula._quantifier != Quantifier.NONE:
                quant_list.append(
                    (formula._quantifier, formula.get_quant_var())
                )
                formula._quantifier = Quantifier.NONE
            quant_list = self.move_quantifiers_to_front(
                formula.get_inside(),
                quant_list
            )
        return quant_list

    def skolemize(self, formula: Formula, data: tuple[str, str]) -> Formula:
        formula_type = formula.get_formula_type()
        if formula_type == Type.BINARY:
            formula.set_left(
                self.skolemize(formula.get_left(), data)
            )
            formula.set_right(
                self.skolemize(formula.get_right(), data)
            )
        elif formula_type == Type.UNARY:
            formula.set_inside(
                self.skolemize(formula.get_inside(), data)
            )
        elif formula_type == Type.FUNCTION:
            inside = formula.get_inside()
            if inside.get_formula_type() != Type.VARIABLE:
                formula.set_inside(
                    self.skolemize(formula.get_inside(), data)
                )
            elif inside.get_var_name() == data[0]:
                prev_var = data[1]
                if prev_var == "":
                    # if there's no quantifiers
                    formula.set_inside(
                        Variable("u")
                    )
                else:
                    # if there's quantifiers outside
                    if inside.get_var_name() != prev_var:
                        formula.set_inside(
                            Function("f", Variable(prev_var))
                        )
        return formula

    def get_prenex(self):
        print("Sub step 1. removing arrows")
        for formula in self._arg:
            self.remove_arrows(formula)

        self.print_argument()
        print("")

        print("Sub step 2. moving negation inward")
        for formula in self._arg:
            formula_type = formula.get_formula_type()
            var_count = formula.get_var_count()

            if formula_type == Type.UNARY:
                formula = self.move_negation_inward(formula, False)
                formula.set_quantifier(formula.get_quantifier())
                formula.set_var_count(var_count)

            if formula_type == Type.BINARY:
                formula = self.move_negation_inward(formula, False)
                formula.set_var_count(var_count)

        self.print_argument()
        print("")

        print("Sub step 3. standardize variables")
        for formula in self._arg:
            var_count = formula.get_var_count()

            for var in var_count:
                self._subscript = 0
                formula = self.standardize_variables(formula, var)

        self.print_argument()
        print("")

        print("Sub step 4. moving all quantifiers to front")
        for formula in self._arg:
            formula.set_quant_list(
                self.move_quantifiers_to_front(formula, [])
            )

        self.print_argument()
        print("")

        print("Sub step 5. Skolemize the formula")
        for formula in self._arg:
            drop_list = []

            # dropping the existentials in the quantifier list
            quant_list = formula.get_quant_list()
            for index, quant_holder in enumerate(quant_list.copy()):
                quantifier = quant_holder[0]
                quant_var = quant_holder[1]
                if len(quant_list) > 1:
                    prev_var = quant_list[index - 1][1]
                else:
                    prev_var = ""
                if (quantifier == Quantifier.EXISTENTIAL
                        and quant_var not in quant_list):
                    drop_list.append((quant_var, prev_var))
                    quant_list.pop(index)
                    formula.set_quant_list(quant_list)

            # skolemize each variable in the formula
            for to_drop in drop_list:
                formula = self.skolemize(formula, to_drop)

        self.print_argument()
        print("")

    def convert_to_conjunctive_normal(self, formula: Formula):
        formula_type = formula.get_formula_type()
        if formula_type == Type.UNARY:
            pass
        elif formula_type == Type.BINARY:
            left_type = formula.left.get_formula_type()
            right_type = formula.right.get_formula_type()
            if left_type == Type.UNARY:
                pass
            elif right_type == Type.UNARY:
                pass
            elif left_type == Type.BINARY and right_type == Type.BINARY:
                pass
            elif left_type == Type.BINARY:
                pass
            elif right_type == Type.BINARY:
                pass

            if formula.connective == Connective.AND:
                pass
            elif formula.connective == Connective.OR:
                pass
        else:
            pass
        return formula

    def populate_clauses(self):
        pass

    def get_clauses(self):
        print("Sub step 1. Dropping all quantifiers")
        for formula in self._arg:
            formula.set_quant_list([])

        self.print_argument()
        print("")

    def check_resolvable(self):
        # check if function name is the same
        # check if one is negated
        # check if it's the same after assignment
        pass

    def get_most_common_var(self):
        pass

    def resolve(self, clauses):
        pass