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
        self.formula_one = exp1
        self.connective = connective
        self.formula_two = exp2
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
    def __init__(self, exp: Expression, quant: Quantifier, neg: bool, var: str):
        super().__init__(Type.UNARY)
        self.quantifier = quant
        self.formula = exp
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
        self.formula.print_expression()

    def set(self, var: str):
        self.formula.set(var)
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

    def compute_prenex_recursively(self, formula: Expression):
        if formula.formulaType == Type.BINARY:
            new_formula_one = self.compute_prenex_recursively(formula.formula_one)
            new_formula_two = self.compute_prenex_recursively(formula.formula_two)
            if formula.connective == Connective.IMPLICATION:
                formula.formula_one = Unary(new_formula_one, Quantifier.NONE, True, "")
                formula.formula_two = new_formula_two
                formula.connective = Connective.OR
            if formula.connective == Connective.BICONDITIONAL:
                formula.formula_one = Binary(
                    new_formula_one,
                    new_formula_two,
                    Connective.AND
                )
                formula.formula_two = Binary(
                    Unary(new_formula_one, Quantifier.NONE, True, ""),
                    Unary(new_formula_two, Quantifier.NONE, True, ""),
                    Connective.AND
                )
                formula.connective = Connective.OR
        if formula.formulaType == Type.UNARY:
            formula.formula = self.compute_prenex_recursively(formula.formula)
        return formula

    def get_prenex(self):
        for formulas in self.arg:
            formula = formulas.pop()
            new_formula = self.compute_prenex_recursively(formula)
            formulas.append(new_formula)

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


def input_commands(commandInput: [], args: [[Expression]]):
    for part in commandInput:
        if part == "print":
            for arg in args:
                arg[len(arg) - 1].print_expression()
                print("")
        if part == "resolve":
            apply_resolution(argument)


def apply_resolution(arg: [Expression]):
    resolver = ResolutionProver(arg)

    print("Negate conclusion yield")
    resolver.negate_conclusion()
    resolver.print_argument()

    resolver.get_prenex()
    resolver.print_argument()


argument = []
for line in fileinput.input(files='test1.txt'):
    inputList = line.split()
    label = inputList[0]
    inputList.pop(0)
    if label == "input":
        argument.append(input_formula(inputList))
    if label == "command":
        input_commands(inputList, argument)
