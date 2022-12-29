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


class Expression(ABC):
    def __init__(self, formula_type: Type):
        self._formula_type = formula_type
        self._var_count = {}
        self._quant_list = []

    @abstractmethod
    def print_expression(self):
        pass

    @abstractmethod
    def set(self, var: str):
        pass

    @abstractmethod
    def set_var_count(self, var_count: {}):
        pass

    def get_formula_type(self):
        return self._formula_type

    def get_var_count(self):
        return self._var_count

    def get_quant_list(self):
        return self._quant_list


class Binary(Expression):
    def __init__(self, left: Expression, right: Expression, connective: Connective):
        super().__init__(Type.BINARY)
        self._left = left
        self._connective = connective
        self._right = right

    def print_expression(self):
        print("(", end="")
        self._left.print_expression()
        if self._connective == Connective.IMPLICATION:
            print(" ⇒ ", end="")
        if self._connective == Connective.BICONDITIONAL:
            print(" ⇔ ", end="")
        if self._connective == Connective.AND:
            print(" ∧ ", end="")
        if self._connective == Connective.OR:
            print(" ∨ ", end="")
        self._right.print_expression()
        print(")", end="")

    def set(self, var: str):
        self._left.set(var)
        self._right.set(var)

    def set_var_count(self, var_count: {}):
        self._var_count = var_count
        self._left.set_var_count(var_count)
        self._right.set_var_count(var_count)


class Unary(Expression):
    def __init__(self, inside: Expression, quant: Quantifier, neg: bool, var: str):
        super().__init__(Type.UNARY)
        self._quantifier = quant
        self._inside = inside
        self._quant_var = var
        self._negation = neg

    def print_expression(self):
        if self._negation:
            print("¬", end="")
        if self._quantifier == Quantifier.EXISTENTIAL:
            print("∃" + self._quant_var, end="")
        if self._quantifier == Quantifier.UNIVERSAL:
            print("∀" + self._quant_var, end="")
        self._inside.print_expression()

    def set(self, var: str):
        self._inside.set(var)

    def set_var_count(self, var_count: {}):
        self._var_count = var_count
        self._inside.set_var_count(var_count)


class Variable(Expression):
    def __init__(self, var_name):
        super().__init__(Type.VARIABLE)
        self._var_name = var_name

    def print_expression(self):
        print(self._var_name, end="")

    def set(self, var_name):
        self._var_name = var_name

    def set_var_count(self, var_count: {}):
        self._var_count = var_count


class Function(Expression):
    def __init__(self, name: str, inside: Expression):
        super().__init__(Type.FUNCTION)
        self._func_name = name
        self._inside = inside

    def print_expression(self):
        print(self._func_name + "(", end="")
        self._inside.print_expression()
        print(")", end="")

    def set(self, var):
        self._inside.set(var)

    def set_var_count(self, var_count: {}):
        self._var_count = var_count
        self._inside.set_var_count(var_count)


class ResolutionProver:
    def __init__(self, arg: [Expression]):
        self._arg = arg
        self._clauses = []
        self._subscript = 0
        self._setOfSupport = []

    def print_argument(self):
        for formulas in self._arg:
            quant_list = formulas[0].get_quant_list()
            if len(quant_list) > 0:
                for item in quant_list:
                    if item[0] == Quantifier.EXISTENTIAL:
                        print("∃" + item[1], end="")
                    if item[0] == Quantifier.UNIVERSAL:
                        print("∀" + item[1], end="")
            formulas[0].print_expression()
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

    def remove_arrows(self, formula: Expression):
        formula_type = formula.get_formula_type()
        if formula_type == Type.BINARY:
            new_left = self.remove_arrows(formula._left)
            new_right = self.remove_arrows(formula._right)
            if formula._connective == Connective.IMPLICATION:
                formula._left = Unary(new_left, Quantifier.NONE, True, "")
                formula._right = new_right
                formula._connective = Connective.OR
            if formula._connective == Connective.BICONDITIONAL:
                formula._left = Binary(
                    new_left,
                    new_right,
                    Connective.AND
                )
                formula._right = Binary(
                    Unary(new_left, Quantifier.NONE, True, ""),
                    Unary(new_right, Quantifier.NONE, True, ""),
                    Connective.AND
                )
                formula._connective = Connective.OR
        if formula_type == Type.UNARY:
            formula._inside = self.remove_arrows(formula._inside)
        return formula

    def move_negation_inward(self, formula: Expression, negation_outside: bool):
        formula_type = formula.get_formula_type()
        if formula_type == Type.BINARY:
            formula._left = self.move_negation_inward(formula._left, negation_outside)
            formula._right = self.move_negation_inward(formula._right, negation_outside)

            if negation_outside and formula._connective == Connective.AND:
                formula._connective = Connective.OR
            elif negation_outside and formula._connective == Connective.OR:
                formula._connective = Connective.AND
        if formula_type == Type.UNARY:
            if negation_outside and formula._negation:
                # if previous negation cancels out, we don't reverse quantifiers no negation passed
                formula._inside = self.move_negation_inward(formula._inside, False)
            elif negation_outside or formula._negation:
                # if previous negates results in a negation, we need to reverse quantifiers and pass the negation
                if formula._quantifier == Quantifier.UNIVERSAL:
                    formula._quantifier = Quantifier.EXISTENTIAL
                elif formula._quantifier == Quantifier.EXISTENTIAL:
                    formula._quantifier = Quantifier.UNIVERSAL
                formula._inside = self.move_negation_inward(formula._inside, True)
            else:
                # if no negation, we don't reverse quantifiers no negation passed
                formula._inside = self.move_negation_inward(formula._inside, False)

        if (negation_outside
                and formula_type != Type.BINARY
                and formula_type != Type.UNARY):
            # if formula is function, and there's a negation, wraps it in a unary with negation
            formula = Unary(formula, Quantifier.NONE, True, "")
        else:
            # if formula is binary or unary, then we are returning to previous, don't add negation
            formula._negation = False

        return formula

    def standardize_variables(self, formula: Expression, var_name: str):
        formula_type = formula.get_formula_type()
        if formula_type == Type.UNARY:
            if formula._quant_var == var_name and formula._quantifier != Quantifier.NONE:
                self._subscript += 1
                formula._quant_var = var_name + str(self._subscript)
            formula._inside = self.standardize_variables(formula._inside, var_name)
        elif formula_type == Type.BINARY:
            formula._left = self.standardize_variables(formula._left, var_name)
            formula._right = self.standardize_variables(formula._right, var_name)
        elif formula_type == Type.FUNCTION:
            if formula._inside._var_name == var_name and self._subscript != 0:
                formula.set(var_name + str(self._subscript))
        else:
            if formula._var_name == var_name:
                formula.set(var_name + str(self._subscript))
        return formula

    def move_quantifiers_to_front(self, formula: Expression, quantList: []):
        formula_type = formula.get_formula_type()
        if formula_type == Type.BINARY:
            quantList = self.move_quantifiers_to_front(formula._left, quantList)
            quantList = self.move_quantifiers_to_front(formula._right, quantList)
        elif formula_type == Type.UNARY:
            if formula._quantifier != Quantifier.NONE:
                quantList.append((formula._quantifier, formula._quant_var))
                formula._quantifier = Quantifier.NONE
            quantList = self.move_quantifiers_to_front(formula._inside, quantList)
        return quantList

    def skolemize(self, formula: Expression, data: tuple[str, str]):
        formula_type = formula.get_formula_type()
        if formula_type == Type.BINARY:
            formula._left = self.skolemize(formula._left, data)
            formula._right = self.skolemize(formula._right, data)
        elif formula_type == Type.UNARY:
            formula._inside = self.skolemize(formula._inside, data)
        elif formula_type == Type.FUNCTION:
            if formula._inside.get_formula_type() != Type.VARIABLE:
                formula._inside = self.skolemize(formula._inside, data)
            elif formula._inside._var_name == data[0]:
                prev_var = data[1]
                if prev_var == "":
                    # if there's no quantifiers
                    variable = Variable("u")
                    formula._inside = variable
                else:
                    # if there's quantifiers outside
                    variable = Variable(prev_var)
                    if formula._inside._var_name != prev_var:
                        function = Function("f", variable)
                        formula._inside = function
        return formula

    def get_prenex(self):
        print("Sub step 1. removing arrows")
        for formulas in self._arg:
            formula = formulas.pop()
            newFormula = self.remove_arrows(formula)
            formulas.append(newFormula)
        self.print_argument()
        print("")

        print("Sub step 2. moving negation inward")
        for formulas in self._arg:
            formula = formulas.pop()
            formula_type = formula.get_formula_type()
            var_count = formula.get_var_count()
            if formula_type == Type.UNARY:
                newFormula = self.move_negation_inward(formula, False)
                newFormula._quantifier = formula._quantifier
                newFormula.set_var_count(var_count)
                formulas.append(newFormula)
            if formula_type == Type.BINARY:
                newFormula = self.move_negation_inward(formula, False)
                newFormula.set_var_count(var_count)
                formulas.append(newFormula)
        self.print_argument()
        print("")

        print("Sub step 3. standardize variables")
        for formulas in self._arg:
            formula = formulas[0]
            var_count = formula.get_var_count()
            for var in var_count:
                self._subscript = 0
                formulas[0] = self.standardize_variables(formula, var)
        self.print_argument()
        print("")

        print("Sub step 4. moving all quantifiers to front")
        for formulas in self._arg:
            formula = formulas[0]
            formula._quant_list = self.move_quantifiers_to_front(formula, [])
        self.print_argument()
        print("")

        print("Sub step 5. Skolemize the formula")
        for formulaHolder in self._arg:
            drop_list = []
            formula = formulaHolder[0]
            for index, quantHolder in enumerate(formula._quant_list.copy()):
                quantifier = quantHolder[0]
                quant_var = quantHolder[1]
                if len(formula._quant_list) > 1:
                    prev_var = formula._quant_list[index - 1][1]
                else:
                    prev_var = ""
                if (quantifier == Quantifier.EXISTENTIAL
                        and quant_var not in formula._quant_list):
                    drop_list.append((quant_var, prev_var))
                    formula._quant_list.pop(index)
            for to_drop in drop_list:
                formulaHolder[0] = self.skolemize(formula, to_drop)
        self.print_argument()
        print("")

    def get_clauses(self):
        pass

    def get_most_common_var(self):
        pass

    def get_clauses(self):
        pass

    def resolve(self, clauses):
        pass


def input_formula(formulaInput: [Expression]) -> [Expression]:
    formula = []
    var_count = {}

    for index, part in enumerate(formulaInput):
        if part == "->":
            right = formula.pop()
            left = formula.pop()

            binary = Binary(left, right, Connective.IMPLICATION)
            formula.append(binary)
        if part == "<->":
            right = formula.pop()
            left = formula.pop()

            binary = Binary(left, right, Connective.BICONDITIONAL)
            formula.append(binary)
        if part == "AND":
            right = formula.pop()
            left = formula.pop()

            binary = Binary(left, right, Connective.AND)
            formula.append(binary)
        if part == "OR":
            right = formula.pop()
            left = formula.pop()

            binary = Binary(left, right, Connective.OR)
            formula.append(binary)
        if part == "FORM":
            func_name = input_list[index + 1]
            var_name = input_list[index + 2]

            if var_name not in var_count:
                var_count[var_name] = 1
            else:
                var_count[var_name] += 1

            variable = Variable(var_name)
            function = Function(func_name, variable)
            formula.append(function)
        if part == "NOT":
            inside = formula.pop()

            unary = Unary(inside, Quantifier.NONE, True, "")
            formula.append(unary)
        if part == "FORALL":
            inside = formula.pop()
            var_name = input_list[index + 1]

            if var_name not in var_count:
                var_count[var_name] = 1

            unary = Unary(inside, Quantifier.UNIVERSAL, False, var_name)
            formula.append(unary)
        if part == "EXIST":
            inside = formula.pop()
            var_name = input_list[index + 1]

            if var_name not in var_count:
                var_count[var_name] = 1

            unary = Unary(inside, Quantifier.EXISTENTIAL, False, var_name)
            formula.append(unary)
        if part == "done":
            break

    formula[0].set_var_count(var_count)
    return formula


def input_commands(command_input: [], args: [[Expression]]):
    for part in command_input:
        if part == "print":
            print("Printing argument")
            for arg in args:
                arg[len(arg) - 1].print_expression()
                print("")
            print("")
        if part == "resolve":
            apply_resolution(argument)


def apply_resolution(arg: [Expression]):
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
for line in fileinput.input(files='test2.txt'):
    input_list = line.split()
    label = input_list[0]
    input_list.pop(0)
    if label == "input":
        argument.append(input_formula(input_list))
    if label == "command":
        input_commands(input_list, argument)
