from abc import ABC, abstractmethod
from enum import Enum
import fileinput


class Quantifier(Enum):
    EXISTENTIAL = 1
    UNIVERSAL = 2
    NONE = 3


class Connective(Enum):
    IMPLICATION = 1
    BICONDITIONAL = 2
    AND = 3
    OR = 4


class Type(Enum):
    UNARY = 1
    BINARY = 2
    FUNCTION = 3
    VARIABLE = 4


class Formula(ABC):
    def __init__(self, formula_type: Type):
        self._formula_type = formula_type
        self._var_count = {}
        self._quant_list = []

    @abstractmethod
    def print_formula(self):
        pass

    @abstractmethod
    def set_var(self, var: str):
        pass

    @abstractmethod
    def set_var_count(self, var_count: {}):
        pass

    def set_quant_list(self, quant_list: []):
        self._quant_list = quant_list

    def get_formula_type(self):
        return self._formula_type

    def get_var_count(self):
        return self._var_count

    def get_quant_list(self):
        return self._quant_list


class Binary(Formula):
    def __init__(
            self,
            left: Formula,
            right: Formula,
            connective: Connective
    ):
        super().__init__(Type.BINARY)
        self._left = left
        self._connective = connective
        self._right = right

    def print_formula(self):
        print("(", end="")
        self._left.print_formula()
        if self._connective == Connective.IMPLICATION:
            print(" ⇒ ", end="")
        if self._connective == Connective.BICONDITIONAL:
            print(" ⇔ ", end="")
        if self._connective == Connective.AND:
            print(" ∧ ", end="")
        if self._connective == Connective.OR:
            print(" ∨ ", end="")
        self._right.print_formula()
        print(")", end="")

    def get_left(self):
        return self._left

    def get_right(self):
        return self._right

    def get_connective(self):
        return self._connective

    def set_var(self, var: str):
        self._left.set_var(var)
        self._right.set_var(var)

    def set_var_count(self, var_count: {}):
        self._var_count = var_count
        self._left.set_var_count(var_count)
        self._right.set_var_count(var_count)

    def set_left(self, left: Formula):
        self._left = left

    def set_connective(self, connective: Connective):
        self._connective = connective

    def set_right(self, right: Formula):
        self._right = right


class Unary(Formula):
    def __init__(
            self,
            inside: Formula,
            quant: Quantifier,
            negation: bool,
            quant_var: str
    ):
        super().__init__(Type.UNARY)
        self._quantifier = quant
        self._inside = inside
        self._quant_var = quant_var
        self._negation = negation

    def print_formula(self):
        if self._negation:
            print("¬", end="")
        if self._quantifier == Quantifier.EXISTENTIAL:
            print("∃" + self._quant_var, end="")
        if self._quantifier == Quantifier.UNIVERSAL:
            print("∀" + self._quant_var, end="")
        self._inside.print_formula()

    def get_quantifier(self):
        return self._quantifier

    def get_inside(self):
        return self._inside

    def get_quant_var(self):
        return self._quant_var

    def set_var(self, var: str):
        self._inside.set_var(var)

    def set_var_count(self, var_count: {}):
        self._var_count = var_count
        self._inside.set_var_count(var_count)

    def set_quantifier(self, quantifier: Quantifier):
        self._quantifier = quantifier

    def set_inside(self, inside: Formula):
        self._inside = inside

    def set_quant_var(self, quant_var: str):
        self._quant_var = quant_var


class Variable(Formula):
    def __init__(self, var_name):
        super().__init__(Type.VARIABLE)
        self._var_name = var_name

    def print_formula(self):
        print(self._var_name, end="")

    def get_var_name(self):
        return self._var_name

    def set_var(self, var_name):
        self._var_name = var_name

    def set_var_count(self, var_count: {}):
        self._var_count = var_count


class Function(Formula):
    def __init__(self, name: str, inside: Formula):
        super().__init__(Type.FUNCTION)
        self._func_name = name
        self._inside = inside

    def print_formula(self):
        print(self._func_name + "(", end="")
        self._inside.print_formula()
        print(")", end="")

    def get_inside(self):
        return self._inside

    def set_var(self, var):
        self._inside.set_var(var)

    def set_var_count(self, var_count: {}):
        self._var_count = var_count
        self._inside.set_var_count(var_count)

    def set_inside(self, inside: Formula):
        self._inside = inside


class ResolutionProver:
    def __init__(self, arg: [Formula]):
        self._arg = arg
        self._clauses = []
        self._setOfSupport = []
        self._subscript = 0

    def print_argument(self):
        for formulas in self._arg:
            quant_list = formulas[0].get_quant_list()
            if len(quant_list) > 0:
                for item in quant_list:
                    if item[0] == Quantifier.EXISTENTIAL:
                        print("∃" + item[1], end="")
                    if item[0] == Quantifier.UNIVERSAL:
                        print("∀" + item[1], end="")
            formulas[0].print_formula()
            print("")

    def print_clauses(self):
        pass

    def negate_conclusion(self):
        conclusion = self._arg.pop().pop()
        unary = Unary(conclusion, Quantifier.NONE, True, "")
        unary.set_var_count(conclusion.get_var_count())
        self._arg.append([unary])

    def check_resolvable(self):
        # check if function name is the same
        # check if one is negated
        # check if it's the same after assignment
        pass

    def remove_arrows(self, formula: Formula):
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

    def move_negation_inward(self, formula: Formula, negation_outside: bool):
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
            if negation_outside and formula._negation:
                # if previous negation cancels out, we don't reverse quantifiers no negation passed
                formula.set_inside(
                    self.move_negation_inward(formula.get_inside(), False)
                )
            elif negation_outside or formula._negation:
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
        else:
            # if formula is binary or unary, then we are returning to previous, don't add negation
            formula._negation = False

        return formula

    def standardize_variables(self, formula: Formula, var_name: str):
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

    def move_quantifiers_to_front(self, formula: Formula, quant_list: []):
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

    def skolemize(self, formula: Formula, data: tuple[str, str]):
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
        for formula_holder in self._arg:
            formula = formula_holder.pop()
            newFormula = self.remove_arrows(formula)
            formula_holder.append(newFormula)

        self.print_argument()
        print("")

        print("Sub step 2. moving negation inward")
        for formula_holder in self._arg:
            formula = formula_holder.pop()
            formula_type = formula.get_formula_type()
            var_count = formula.get_var_count()

            if formula_type == Type.UNARY:
                newFormula = self.move_negation_inward(formula, False)
                newFormula.set_quantifier(formula.get_quantifier())
                newFormula.set_var_count(var_count)
                formula_holder.append(newFormula)

            if formula_type == Type.BINARY:
                newFormula = self.move_negation_inward(formula, False)
                newFormula.set_var_count(var_count)
                formula_holder.append(newFormula)

        self.print_argument()
        print("")

        print("Sub step 3. standardize variables")
        for formula_holder in self._arg:
            formula = formula_holder[0]
            var_count = formula.get_var_count()

            for var in var_count:
                self._subscript = 0
                formula_holder[0] = self.standardize_variables(formula, var)

        self.print_argument()
        print("")

        print("Sub step 4. moving all quantifiers to front")
        for formula_holder in self._arg:
            formula = formula_holder[0]
            formula.set_quant_list(
                self.move_quantifiers_to_front(formula, [])
            )

        self.print_argument()
        print("")

        print("Sub step 5. Skolemize the formula")
        for formula_holder in self._arg:
            drop_list = []
            formula = formula_holder[0]

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

            for to_drop in drop_list:
                formula_holder[0] = self.skolemize(formula, to_drop)

        self.print_argument()
        print("")

    def get_clauses(self):
        pass

    def get_most_common_var(self):
        pass

    def resolve(self, clauses):
        pass


def input_formula(formulaInput: [Formula]) -> [Formula]:
    formula = []
    var_count = {}

    for index, part in enumerate(formulaInput):
        if part == "->":
            right = formula.pop()
            left = formula.pop()

            formula.append(
                Binary(left, right, Connective.IMPLICATION)
            )
        if part == "<->":
            right = formula.pop()
            left = formula.pop()

            formula.append(
                Binary(left, right, Connective.BICONDITIONAL)
            )
        if part == "AND":
            right = formula.pop()
            left = formula.pop()

            formula.append(
                Binary(left, right, Connective.AND)
            )
        if part == "OR":
            right = formula.pop()
            left = formula.pop()

            formula.append(
                Binary(left, right, Connective.OR)
            )
        if part == "FORM":
            func_name = input_list[index + 1]
            var_name = input_list[index + 2]

            if var_name not in var_count:
                var_count[var_name] = 1
            else:
                var_count[var_name] += 1

            formula.append(
                Function(func_name, Variable(var_name))
            )
        if part == "NOT":
            inside = formula.pop()

            formula.append(
                Unary(inside, Quantifier.NONE, True, "")
            )
        if part == "FORALL":
            inside = formula.pop()
            var_name = input_list[index + 1]

            if var_name not in var_count:
                var_count[var_name] = 1

            formula.append(
                Unary(inside, Quantifier.UNIVERSAL, False, var_name)
            )
        if part == "EXIST":
            inside = formula.pop()
            var_name = input_list[index + 1]

            if var_name not in var_count:
                var_count[var_name] = 1

            formula.append(
                Unary(inside, Quantifier.EXISTENTIAL, False, var_name)
            )
        if part == "done":
            break

    formula[0].set_var_count(var_count)
    return formula


def input_commands(command_input: [], args: [[Formula]]):
    for part in command_input:
        if part == "print":
            print("Printing argument")
            for arg in args:
                arg[len(arg) - 1].print_formula()
                print("")
            print("")
        if part == "resolve":
            apply_resolution(argument)


def apply_resolution(arg: [Formula]):
    resolver = ResolutionProver(arg)

    print("Executing Step 1. Negate conclusion")
    resolver.negate_conclusion()
    print("Step 1 completed")
    resolver.print_argument()
    print("")

    print("Executing Step 2. Turning arguments into ∃-free Prenex Normal Form")
    resolver.get_prenex()
    print("Step 2 completed")
    resolver.print_argument()
    print("")

    print("Executing Step 3. Getting clauses from Prenex Normal Form")
    resolver.get_clauses()
    print("Step 2 completed")
    resolver.print_argument()
    print("")


argument = []
for line in fileinput.input(files='test1.txt'):
    input_list = line.split()
    label = input_list[0]
    input_list.pop(0)
    if label == "input":
        argument.append(input_formula(input_list))
    if label == "command":
        input_commands(input_list, argument)
