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
        self.expVarCount = {}
        self.quantList = []

    @abstractmethod
    def print_expression(self):
        pass

    @abstractmethod
    def set(self, var: str):
        pass

    def set_var_list(self, expVarCount: {}):
        self.expVarCount = expVarCount


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
        self.quantVar = var
        self.negation = neg
        self.valueSet = True

    def print_expression(self):
        if self.negation:
            print("¬", end="")
        if self.quantifier == Quantifier.EXISTENTIAL:
            print("∃" + self.quantVar, end="")
        if self.quantifier == Quantifier.UNIVERSAL:
            print("∀" + self.quantVar, end="")
        self.inside.print_expression()

    def set(self, var: str):
        self.inside.set(var)
        self.valueSet = True


class Variable(Expression):
    def __init__(self, var):
        super().__init__(Type.VARIABLE)
        self.varName = var
        self.valueSet = False

    def print_expression(self):
        print(self.varName, end="")

    def set(self, var):
        self.varName = var


class Function(Expression):
    def __init__(self, name: str, exp: Expression):
        super().__init__(Type.FUNCTION)
        self.name = name
        self.exp = exp

    def print_expression(self):
        print(self.name + "(", end="")
        self.exp.print_expression()
        print(")", end="")

    def set(self, var):
        self.exp.set(var)


class ResolutionProver:
    def __init__(self, arg: [Expression]):
        self.arg = arg
        self.currVarCount = 0
        self.setOfSupport = []

    def print_argument(self):
        for formulas in self.arg:
            if len(formulas[0].quantList) > 0:
                for item in formulas[0].quantList:
                    if item[0] == Quantifier.EXISTENTIAL:
                        print("∃" + item[1], end="")
                    if item[0] == Quantifier.UNIVERSAL:
                        print("∀" + item[1], end="")
            formulas[0].print_expression()
            print("")

    def negate_conclusion(self):
        conclusion = self.arg.pop().pop()
        unary = Unary(conclusion, Quantifier.NONE, True, "")
        unary.set_var_list(conclusion.expVarCount)
        self.arg.append([unary])

    def check_resolvable(self):
        # check if function name is the same
        # check if one is negated
        # check if it's the same after assignment
        pass

    def remove_arrows(self, formula: Expression):
        if formula.formulaType == Type.BINARY:
            new_left = self.remove_arrows(formula.left)
            new_right = self.remove_arrows(formula.right)
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
            formula.inside = self.remove_arrows(formula.inside)
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
            if negation_outside and formula.negation:
                # if previous negation cancels out, we don't reverse quantifiers no negation passed
                formula.inside = self.move_negation_inward(formula.inside, False)
            elif negation_outside or formula.negation:
                # if previous negates results in a negation, we need to reverse quantifiers and pass the negation
                if formula.quantifier == Quantifier.UNIVERSAL:
                    formula.quantifier = Quantifier.EXISTENTIAL
                elif formula.quantifier == Quantifier.EXISTENTIAL:
                    formula.quantifier = Quantifier.UNIVERSAL
                formula.inside = self.move_negation_inward(formula.inside, True)
            else:
                # if no negation, we don't reverse quantifiers no negation passed
                formula.inside = self.move_negation_inward(formula.inside, False)

        if (negation_outside
                and formula.formulaType != Type.BINARY
                and formula.formulaType != Type.UNARY):
            # if formula is function, and there's a negation, wraps it in a unary with negation
            formula = Unary(formula, Quantifier.NONE, True, "")
        else:
            # if formula is binary or unary, then we are returning to previous, don't add negation
            formula.negation = False

        return formula

    def standardize_variables(self, formula: Expression, var: str):
        if formula.formulaType == Type.UNARY:
            if formula.quantVar == var and formula.quantifier != Quantifier.NONE:
                self.currVarCount += 1
                formula.quantVar = var + str(self.currVarCount)
            formula.inside = self.standardize_variables(formula.inside, var)
        elif formula.formulaType == Type.BINARY:
            formula.left = self.standardize_variables(formula.left, var)
            formula.right = self.standardize_variables(formula.right, var)
        elif formula.formulaType == Type.FUNCTION:
            if formula.exp.varName == var and self.currVarCount != 0:
                formula.set(var + str(self.currVarCount))
        else:
            if formula.varName == var:
                formula.set(var + str(self.currVarCount))
        return formula

    def move_quantifiers_to_front(self, formula: Expression, quantList: []):
        if formula.formulaType == Type.BINARY:
            quantList = self.move_quantifiers_to_front(formula.left, quantList)
            quantList = self.move_quantifiers_to_front(formula.right, quantList)
        elif formula.formulaType == Type.UNARY:
            if formula.quantifier != Quantifier.NONE:
                quantList.append((formula.quantifier, formula.quantVar))
                formula.quantifier = Quantifier.NONE
            quantList = self.move_quantifiers_to_front(formula.inside, quantList)
        return quantList

    def skolemize(self, formula: Expression, toDrop: []):
        if formula.formulaType == Type.BINARY:
            pass
        elif formula.formulaType == Type.UNARY:
            pass
        return formula

    def get_prenex(self):
        print("Sub step 1. removing arrows")
        for formulas in self.arg:
            formula = formulas.pop()
            newFormula = self.remove_arrows(formula)
            formulas.append(newFormula)
        self.print_argument()
        print("")

        print("Sub step 2. moving negation inward")
        for formulas in self.arg:
            formula = formulas.pop()
            if formula.formulaType == Type.UNARY:
                newFormula = self.move_negation_inward(formula, False)
                newFormula.quantifier = formula.quantifier
                newFormula.set_var_list(formula.expVarCount)
                formulas.append(newFormula)
            if formula.formulaType == Type.BINARY:
                newFormula = self.move_negation_inward(formula, False)
                newFormula.set_var_list(formula.expVarCount)
                formulas.append(newFormula)
        self.print_argument()
        print("")

        print("Sub step 3. standardize variables")
        for formulas in self.arg:
            formula = formulas[0]
            for var in formula.expVarCount:
                self.currVarCount = 0
                formulas[0] = self.standardize_variables(formula, var)
        self.print_argument()
        print("")

        print("Sub step 4. moving all quantifiers to front")
        for formulas in self.arg:
            formula = formulas[0]
            formula.quantList = self.move_quantifiers_to_front(formula, [])
        self.print_argument()
        print("")

        print("Sub step 5. Skolemize the formula")
        for formulaHolder in self.arg:
            toDrop = []
            formula = formulaHolder[0]
            for quantHolder in formula.quantList:
                if (quantHolder[0] == Quantifier.EXISTENTIAL
                        and quantHolder[1] not in formula.quantList):
                    toDrop.append(quantHolder[1])
            formulaHolder[0] = self.skolemize(formula, toDrop)
        self.print_argument()
        print("")

    def get_most_common_var(self):
        pass

    def get_clauses(self):
        pass

    def resolve(self, clauses):
        pass


def input_formula(formulaInput: [Expression]) -> [Expression]:
    formula = []
    var_list = {}

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
            func_name = inputList[index + 1]
            var_name = inputList[index + 2]

            if var_name not in var_list:
                var_list[var_name] = 1
            else:
                var_list[var_name] += 1

            variable = Variable(var_name)
            function = Function(func_name, variable)
            formula.append(function)
        if part == "NOT":
            inside = formula.pop()

            unary = Unary(inside, Quantifier.NONE, True, "")
            formula.append(unary)
        if part == "FORALL":
            inside = formula.pop()
            var_name = inputList[index + 1]

            if var_name not in var_list:
                var_list[var_name] = 1

            unary = Unary(inside, Quantifier.UNIVERSAL, False, var_name)
            formula.append(unary)
        if part == "EXIST":
            inside = formula.pop()
            var_name = inputList[index + 1]

            if var_name not in var_list:
                var_list[var_name] = 1

            unary = Unary(inside, Quantifier.EXISTENTIAL, False, var_name)
            formula.append(unary)
        if part == "done":
            break

    formula[0].set_var_list(var_list)
    return formula


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
