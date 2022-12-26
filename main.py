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


class Expression(ABC):
    @abstractmethod
    def print_expression(self):
        pass

    @abstractmethod
    def set(self, var: str):
        pass


class Binary(Expression):
    def __init__(self, e1: Expression, e2: Expression, c: Connective):
        self.formula_one = e1
        self.connective = c
        self.formula_two = e2
        self.valueSet = False

    def print_expression(self):
        print("(", end="")
        self.formula_one.print_expression()
        if self.connective == Connective.IMPLICATION:
            print(" ⇒ ", end="")
        if self.connective == Connective.BICONDITIONAL:
            print(" ⇔ ", end="")
        if self.connective == Connective.AND:
            print(" ∧ ", end="")
        if self.connective == Connective.OR:
            print(" ∨ ", end="")
        self.formula_two.print_expression()
        print(")", end="")

    def set(self, var: str):
        self.formula_one.set(var)
        self.formula_two.set(var)
        self.valueSet = True


class Unary(Expression):
    def __init__(self, e: Expression, q: Quantifier, n: bool, v: str):
        self.quantifier = q
        self.formula = e
        self.variable = v
        self.negation = n
        self.valueSet = True

    def print_expression(self):
        if self.negation:
            print("¬", end="")
        if self.quantifier == Quantifier.EXISTENTIAL:
            print("∃" + self.variable, end="")
        if self.quantifier == Quantifier.UNIVERSAL:
            print("∀" + self.variable, end="")
        self.formula.print_expression()

    def set(self, var: str):
        self.formula.set(var)
        self.valueSet = True


class Variable(Expression):
    def __init__(self, var):
        self.var = var
        self.valueSet = False

    def print_expression(self):
        print(self.var, end="")

    def set(self, var):
        self.var = var


class Function(Expression):
    def __init__(self, name: str, v: Variable):
        self.name = name
        self.variable = v

    def print_expression(self):
        print(self.name + "(", end="")
        self.variable.print_expression()
        print(")", end="")

    def set(self, var):
        self.variable.set(var)


class ResolutionProver:
    def __init__(self):
        self.setOfSupport = []

    def check_resolvable(self):
        # check if function name is the same
        # check if one is negated
        # check if it's the same after assignment
        pass

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
            second = f.pop()
            second.print_expression()
            first = f.pop()

            binary = Binary(first, second, Connective.IMPLICATION)
            f.append(binary)
        if part == "<->":
            second = f.pop()
            first = f.pop()

            binary = Binary(first, second, Connective.BICONDITIONAL)
            f.append(binary)
        if part == "AND":
            second = f.pop()
            first = f.pop()

            binary = Binary(first, second, Connective.AND)
            f.append(binary)
        if part == "OR":
            second = f.pop()
            first = f.pop()

            binary = Binary(first, second, Connective.OR)
            f.append(binary)
        if part == "FORM":
            func_name = inputList[index + 1]
            var_name = inputList[index + 2]

            variable = Variable(var_name)
            function = Function(func_name, variable)
            f.append(function)
        if part == "NOT":
            first = f.pop()

            unary = Unary(first, Quantifier.NONE, True, "")
            f.append(unary)
        if part == "FORALL":
            first = f.pop()

            unary = Unary(first, Quantifier.UNIVERSAL, False, inputList[index + 1])
            f.append(unary)
        if part == "EXIST":
            first = f.pop()

            unary = Unary(first, Quantifier.EXISTENTIAL, False, inputList[index + 1])
            f.append(unary)
        if part == "done":
            break
    return f


def input_commands(commandInput: [], fs: [[Expression]]):
    for part in commandInput:
        if part == "print":
            for f in fs:
                f[len(f) - 1].print_expression()
                print("")


formulas = []
for line in fileinput.input(files='test1.txt'):
    inputList = line.split()
    label = inputList[0]
    inputList.pop(0)
    if label == "input":
        formulas.append(input_formula(inputList))
    if label == "command":
        input_commands(inputList, formulas)
