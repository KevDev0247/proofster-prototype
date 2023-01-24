from enums import Connective, Type, Quantifier
from formula import Unary, Binary, Variable, Function, Formula


def print_clause(clause_group: [[Formula]]):
    for c, clause in enumerate(clause_group):
        for f, formula in enumerate(clause):
            formula.print_formula()
            if f < len(clause) - 1:
                print(" ∨ ", end="")
        if c < len(clause_group) - 1:
            print(", ", end="")
    print("")


class PreProcessor:
    def __init__(self, arg: [Formula]):
        self._arg = arg
        self._premises = []
        self._negated_conclusion = []
        self._subscript = 0

    def get_arg(self):
        return self._arg

    def get_premises(self):
        return self._premises

    def get_negated_conclusion(self):
        return self._negated_conclusion

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
        for p, premise in enumerate(self._premises):
            print("Premise " + str(p+1) + ": ", end="")
            print_clause(premise)
        print("¬Conclusion ", end="")
        print_clause(self._negated_conclusion[0])

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
            if formula.get_quantifier() != Quantifier.NONE:
                quant_list.append(
                    (formula.get_quantifier(), formula.get_quant_var())
                )
                formula.set_quantifier(Quantifier.NONE)
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

    def convert_to_prenex(self):
        print("Sub step 1. removing arrows")
        for f, formula in enumerate(self._arg):
            self._arg[f] = self.remove_arrows(formula)

        self.print_argument()
        print("")

        print("Sub step 2. moving negation inward")
        for f, formula in enumerate(self._arg):
            formula_type = formula.get_formula_type()
            var_count = formula.get_var_count()

            # need to refactor the var_count set logic
            if formula_type == Type.UNARY:
                self._arg[f] = self.move_negation_inward(formula, False)
                self._arg[f].set_quantifier(formula.get_quantifier())
                self._arg[f].set_var_count(var_count)

            if formula_type == Type.BINARY:
                self._arg[f] = self.move_negation_inward(formula, False)
                self._arg[f].set_var_count(var_count)

        self.print_argument()
        print("")

        print("Sub step 3. standardize variables")
        for f, formula in enumerate(self._arg):
            var_count = formula.get_var_count()

            for var in var_count:
                self._subscript = 0
                self._arg[f] = self.standardize_variables(formula, var)

        self.print_argument()
        print("")

        print("Sub step 4. moving all quantifiers to front")
        for f, formula in enumerate(self._arg):
            self._arg[f].set_quant_list(
                self.move_quantifiers_to_front(formula, [])
            )

        self.print_argument()
        print("")

        print("Sub step 5. skolemize the formula")
        for f, formula in enumerate(self._arg):
            drop_list = []

            # dropping the existentials in the quantifier list
            quant_list = formula.get_quant_list()
            for q, quant_holder in enumerate(quant_list.copy()):
                quantifier = quant_holder[0]
                quant_var = quant_holder[1]
                if len(quant_list) > 1:
                    prev_var = quant_list[q - 1][1]
                else:
                    prev_var = ""
                if (quantifier == Quantifier.EXISTENTIAL
                        and quant_var not in quant_list):
                    drop_list.append((quant_var, prev_var))
                    quant_list.pop(q)
                    self._arg[f].set_quant_list(quant_list)

            # skolemize each variable in the formula
            for to_drop in drop_list:
                self._arg[f] = self.skolemize(formula, to_drop)

        self.print_argument()
        print("")

    def convert_binary_formula_to_cnf(self, formula: Formula, self_check: bool) -> Formula:
        left = formula.get_left()
        right = formula.get_right()
        left_type = left.get_formula_type()
        right_type = right.get_formula_type()

        if (left_type == Type.BINARY
                and formula.get_connective() == Connective.OR
                and left.get_connective() == Connective.AND):
            if self_check:
                # convert the current binary formula to cnf
                formula = self.convert_to_cnf(formula)
            else:
                # perform basic conversion procedure, but won't result a cnf
                formula.set_left(
                    Binary(
                        self.convert_to_cnf(left.get_left()),
                        self.convert_to_cnf(right),
                        Connective.OR
                    )
                )
                formula.set_right(
                    Binary(
                        self.convert_to_cnf(left.get_right()),
                        self.convert_to_cnf(right),
                        Connective.OR
                    )
                )
                formula.set_connective(Connective.AND)
        if (right_type == Type.BINARY
                and formula.get_connective() == Connective.OR
                and right.get_connective() == Connective.AND):
            if self_check:
                # convert the current binary formula to cnf
                formula = self.convert_to_cnf(formula)
            else:
                # perform basic conversion procedure, but won't result a cnf
                formula.set_left(
                    Binary(
                        self.convert_to_cnf(left),
                        self.convert_to_cnf(right.get_left()),
                        Connective.OR
                    )
                )
                formula.set_right(
                    Binary(
                        self.convert_to_cnf(left),
                        self.convert_to_cnf(right.get_right()),
                        Connective.OR
                    )
                )
                formula.set_connective(Connective.AND)

        if not self_check:
            # make another recursive call to ensure both sides are in CNF
            formula.set_left(self.convert_to_cnf(formula.get_left()))
            formula.set_right(self.convert_to_cnf(formula.get_right()))
        return formula

    def convert_to_cnf(self, formula: Formula) -> Formula:
        if formula.get_formula_type() == Type.UNARY:
            if formula.get_inside().get_formula_type() == Type.FUNCTION:
                formula.get_inside().set_negation(formula.get_negation())
            # recursively search the inside of unary to perform the conversion procedure
            formula = self.convert_to_cnf(formula.get_inside())
        if formula.get_formula_type() == Type.BINARY:
            # convert the two sides of binary into CNF and change connective
            formula = self.convert_binary_formula_to_cnf(formula, False)
            # convert the newly formed binary to CNF
            formula = self.convert_binary_formula_to_cnf(formula, True)
        return formula

    def populate_clause(self, formula: Formula, clause: [Formula]) -> [Formula]:
        if formula.get_formula_type() == Type.BINARY:
            clause = self.populate_clause(formula.get_left(), clause)
            clause = self.populate_clause(formula.get_right(), clause)
            return clause
        else:
            clause.append(formula)
            return clause

    def populate_clause_group(self, formula: Formula, clause_group: [[Formula]]) -> bool:
        if formula.get_formula_type() != Type.BINARY:
            return True
        else:
            if (formula.get_connective() == Connective.OR
                    and self.populate_clause_group(formula.get_left(), clause_group)
                    and self.populate_clause_group(formula.get_right(), clause_group)):
                return True
            elif formula.get_connective() == Connective.AND:
                if self.populate_clause_group(formula.get_left(), clause_group):
                    new_clause = []
                    new_clause = self.populate_clause(
                        formula.get_left(), new_clause
                    )
                    clause_group.append(new_clause)
                if self.populate_clause_group(formula.get_right(), clause_group):
                    new_clause = []
                    new_clause = self.populate_clause(
                        formula.get_right(), new_clause
                    )
                    clause_group.append(new_clause)
                return False

    def convert_to_clauses(self) -> [Formula]:
        print("Sub step 1. dropping all quantifiers")
        for f, formula in enumerate(self._arg):
            self._arg[f].set_quant_list([])

        self.print_argument()
        print("")

        print("Sub step 2. converting to Conjunctive Normal Form")
        for f, formula in enumerate(self._arg):
            self._arg[f] = self.convert_to_cnf(formula)

        self.print_argument()
        print("")

        print("Sub step 3. converting to clauses")
        for f, formula in enumerate(self._arg):
            clause_group = []
            if self.populate_clause_group(formula, clause_group):
                new_clause = []
                new_clause = self.populate_clause(formula, new_clause)
                clause_group.append(new_clause)

            if f < len(self._arg) - 1:
                self._premises.append(clause_group)
            elif f == len(self._arg) - 1:
                self._negated_conclusion.append(clause_group)

        self.print_clauses()
        print("")

        clauses = []
        for premise in self._premises:
            for clause in premise:
                clauses.append(clause)
        clauses.append(self._negated_conclusion[0])

        return clauses
