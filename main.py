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
    def __init__(self, formulaType: Type):
        self.formulaType = formulaType

    @abstractmethod
    def print_expression(self):
        pass

    @abstractmethod
    def set(self, var: str):
        pass


class Binary(Expression):
    def __init__(self, exp1: Expression, exp2: Expression, connective: Connective):
        super().__init__(Type.BINARY)
        self.left = exp1
        self.connective = connective
        self.right = exp2
        self.valueSet = False

    def print_expression(self):
        print("(", end="")
        self.left.print_expression()
        if self.connective == Connective.IMPLICATION:
            print(" ⇒ ", end="")
        if self.connective == Connective.BICONDITIONAL:
            print(" ⇔ ", end="")
        if self.connective == Connective.AND:
            print(" ∧ ", end="")
        if self.connective == Connective.OR:
            print(" ∨ ", end="")
        self.right.print_expression()
        print(")", end="")

    def set(self, var: str):
        self.left.set(var)
        self.right.set(var)
        self.valueSet = True


class Unary(Expression):
    def __init__(self, exp: Expression, quant: Quantifier, neg: bool, var: str):
        super().__init__(Type.UNARY)
        self.quantifier = quant
        self.inside = exp
        self.variable = var
        self.negation = neg
        self.valueSet = True

    def print_expression(self):
        if self.negation:
            print("¬", end="")
        if self.quantifier == Quantifier.EXISTENTIAL:
            print("∃" + self.variable, end="")
        if self.quantifier == Quantifier.UNIVERSAL:
            print("∀" + self.variable, end="")
        self.inside.print_expression()

    def set(self, var: str):
        self.inside.set(var)
        self.valueSet = True


class Variable(Expression):
    def __init__(self, var):
        super().__init__(Type.VARIABLE)
        self.var = var
        self.valueSet = False

    def print_expression(self):
        print(self.var, end="")

    def set(self, var):
        self.var = var


class Function(Expression):
    def __init__(self, name: str, var: Variable):
        super().__init__(Type.FUNCTION)
        self.name = name
        self.variable = var

    def print_expression(self):
        print(self.name + "(", end="")
        self.variable.print_expression()
        print(")", end="")

    def set(self, var):
        self.variable.set(var)


class ResolutionProver:
    def __init__(self, arg: [Expression]):
        self.arg = arg
        self.setOfSupport = []

    def print_argument(self):
        for formulas in self.arg:
            formulas[0].print_expression()
            print("")

    def negate_conclusion(self):
        conclusion = self.arg.pop().pop()
        unary = Unary(conclusion, Quantifier.NONE, True, "")
        self.arg.append([unary])

    def check_resolvable(self):
        # check if function name is the same
        # check if one is negated
        # check if it's the same after assignment
        pass

    def remove_arrows_recursively(self, formula: Expression):
        if formula.formulaType == Type.BINARY:
            new_left = self.remove_arrows_recursively(formula.left)
            new_right = self.remove_arrows_recursively(formula.right)
            if formula.connective == Connective.IMPLICATION:
                formula.left = Unary(new_left, Quantifier.NONE, True, "")
                formula.right = new_right
                formula.connective = Connective.OR
            if formula.connective == Connective.BICONDITIONAL:
                formula.left = Binary(
                    new_left,
                    new_right,
                    Connective.AND
                )
                formula.right = Binary(
                    Unary(new_left, Quantifier.NONE, True, ""),
                    Unary(new_right, Quantifier.NONE, True, ""),
                    Connective.AND
                )
                formula.connective = Connective.OR
        if formula.formulaType == Type.UNARY:
            formula.inside = self.remove_arrows_recursively(formula.inside)
        return formula

    def move_negation_inward(self, formula: Expression, negation_outside: bool):
        if formula.formulaType == Type.BINARY:
            formula.left = self.move_negation_inward(formula.left, negation_outside)
            formula.right = self.move_negation_inward(formula.right, negation_outside)

            if negation_outside and formula.connective == Connective.AND:
                formula.connective = Connective.OR
            elif negation_outside and formula.connective == Connective.OR:
                formula.connective = Connective.AND
        if formula.formulaType == Type.UNARY:
            formula_negated = formula.negation
            if negation_outside and formula_negated:
                formula.inside = self.move_negation_inward(formula.inside, False)
            elif negation_outside or formula_negated:
                if formula.quantifier == Quantifier.UNIVERSAL:
                    formula.quantifier = Quantifier.EXISTENTIAL
                elif formula.quantifier == Quantifier.EXISTENTIAL:
                    formula.quantifier = Quantifier.UNIVERSAL
                formula.inside = self.move_negation_inward(formula.inside, True)
            else:
                formula.inside = self.move_negation_inward(formula.inside, False)

        if (negation_outside
                and formula.formulaType != Type.BINARY
                and formula.formulaType != Type.UNARY):
            formula = Unary(formula, Quantifier.NONE, True, "")
        else:
            formula.negation = False

        return formula

    def get_prenex(self):
        print("Executing Sub step 1. removing arrows")
        for formulas in self.arg:
            formula = formulas.pop()
            new_formula = self.remove_arrows_recursively(formula)
            formulas.append(new_formula)
        self.print_argument()

        print("Executing Sub step 2. moving negation inward")
        for formulas in self.arg:
            formula = formulas.pop()
            if formula.formulaType == Type.UNARY:
                new_formula = self.move_negation_inward(formula.inside, formula.negation)
                formulas.append(new_formula)
            if formula.formulaType == Type.BINARY:
                new_formula = self.move_negation_inward(formula, False)
                formulas.append(new_formula)
        self.print_argument()
        print("")

    def get_most_common_var(self):
        pass

    def get_clauses(self):
        pass

    def resolve(self, clauses):
        pass


def input_formula(formulaInput: [Expression]) -> [Expression]:
    f = []
    for index, part in enumerate(formulaInput):
        if part == "->":
            right = f.pop()
            left = f.pop()

            binary = Binary(left, right, Connective.IMPLICATION)
            f.append(binary)
        if part == "<->":
            right = f.pop()
            left = f.pop()

            binary = Binary(left, right, Connective.BICONDITIONAL)
            f.append(binary)
        if part == "AND":
            right = f.pop()
            left = f.pop()

            binary = Binary(left, right, Connective.AND)
            f.append(binary)
        if part == "OR":
            right = f.pop()
            left = f.pop()

            binary = Binary(left, right, Connective.OR)
            f.append(binary)
        if part == "FORM":
            func_name = inputList[index + 1]
            var_name = inputList[index + 2]

            variable = Variable(var_name)
            function = Function(func_name, variable)
            f.append(function)
        if part == "NOT":
            inside = f.pop()

            unary = Unary(inside, Quantifier.NONE, True, "")
            f.append(unary)
        if part == "FORALL":
            inside = f.pop()

            unary = Unary(inside, Quantifier.UNIVERSAL, False, inputList[index + 1])
            f.append(unary)
        if part == "EXIST":
            inside = f.pop()

            unary = Unary(inside, Quantifier.EXISTENTIAL, False, inputList[index + 1])
            f.append(unary)
        if part == "done":
            break
    return f


def input_commands(commandInput: [], args: [[Expression]]):
    for part in commandInput:
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


argument = []
for line in fileinput.input(files='test2.txt'):
    inputList = line.split()
    label = inputList[0]
    inputList.pop(0)
    if label == "input":
        argument.append(input_formula(inputList))
    if label == "command":
        input_commands(inputList, argument)
