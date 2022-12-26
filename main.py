from abc import ABC, abstractmethod
from enum import Enum


class Quantifier(Enum):
    EXISTENTIAL = 1
    UNIVERSAL = 2
    NONE = 3


class Connective(Enum):
    IMPLICATION = 1
    BICONDITIONAL = 2


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
        print("(")
        self.formula_one.print_expression()
        if self.connective == Connective.IMPLICATION:
            print(" ⇒ ")
        if self.connective == Connective.BICONDITIONAL:
            print(" ⇔ ")
        self.formula_two.print_expression()
        print(")")

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
            print("¬")
        if self.quantifier != Quantifier.EXISTENTIAL:
            print("∃" + self.variable)
        if self.quantifier != Quantifier.UNIVERSAL:
            print("∀" + self.variable)
        print("(")
        self.formula.print_expression()
        print(")")

    def set(self, var: str):
        self.formula.set(var)
        self.valueSet = True


class Variable(Expression):
    def __init__(self, var):
        self.var = var
        self.valueSet = False

    def print_expression(self):
        print(self.var)

    def set(self, var):
        self.var = var


class Function(Expression):
    def __init__(self, name: str, variable: Variable):
        self.name = name
        self.variable = variable

    def print_expression(self):
        print(self.name + "(")
        self.variable.print_expression()
        print(")")

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


formula = []

print("Enter your formula: ")
inputList = input().split()
for index, part in enumerate(inputList):
    if part == "->":
        second = formula.pop()
        first = formula.pop()

        binary = Binary(first, second, Connective.IMPLICATION)
        formula.append(binary)
    if part == "<->":
        second = formula.pop()
        first = formula.pop()

        binary = Binary(first, second, Connective.BICONDITIONAL)
        formula.append(binary)
    if part == "NEG":
        first = formula.pop()

        unary = Unary(first, Quantifier.NONE, True, "")
        formula.append(unary)
    if part == "forall":
        first = formula.pop()

        unary = Unary(first, Quantifier.UNIVERSAL, False, inputList[index + 1])
        formula.append(unary)
    if part == "exist":
        first = formula.pop()

        unary = Unary(first, Quantifier.EXISTENTIAL, False, inputList[index + 1])
        formula.append(unary)
    if part == "done":
        break

