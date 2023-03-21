import fileinput
from typing import List

from enums import Connective, Quantifier, Type
from formula import Unary, Binary, Variable, Function, Formula
from preprocessor import PreProcessor
from prover import ResolutionProver


class Shared:
    def __init__(self):
        self._input_complete = False
        self._arg = []
        self._premises = []
        self._negated_conclusion = []
        self._clauses = []

    def print_arg(self):
        print("Printing ...")
        for formula in self._arg:
            formula.print_formula()
            print("")
        print("")

    def set_input_complete(self, input_complete):
        self._input_complete = input_complete

    def set_arg(self, arg):
        self._arg = arg

    def set_premises(self, premises: [[Formula]]):
        self._premises = premises

    def set_negated_conclusion(self, negated_conclusion: [[Formula]]):
        self._negated_conclusion = negated_conclusion

    def set_clauses(self, clauses: [Formula]):
        self._clauses = clauses

    def get_input_complete(self):
        return self._input_complete

    def get_arg(self):
        return self._arg

    def get_premises(self):
        return self._premises

    def get_negated_conclusion(self):
        return self._negated_conclusion

    def get_clauses(self):
        return self._clauses


def input_formula(formula_input: [str]) -> Formula:
    formula_holder = []
    var_count = {}

    for p, part in enumerate(formula_input):
        if part == "->":
            right = formula_holder.pop()
            left = formula_holder.pop()

            formula_holder.append(
                Binary(left, right, Connective.IMPLICATION)
            )
        if part == "<->":
            right = formula_holder.pop()
            left = formula_holder.pop()

            formula_holder.append(
                Binary(left, right, Connective.BICONDITIONAL)
            )
        if part == "AND":
            right = formula_holder.pop()
            left = formula_holder.pop()

            formula_holder.append(
                Binary(left, right, Connective.AND)
            )
        if part == "OR":
            right = formula_holder.pop()
            left = formula_holder.pop()

            formula_holder.append(
                Binary(left, right, Connective.OR)
            )
        if part == "FORM":
            func_name = formula_input[p + 1]
            var_name = formula_input[p + 2]

            if var_name not in var_count:
                var_count[var_name] = 1
            else:
                var_count[var_name] += 1

            formula_holder.append(
                Function(func_name, Variable(var_name))
            )
        if part == "NOT":
            inside = formula_holder.pop()

            formula_holder.append(
                Unary(inside, Quantifier.NONE, True, "")
            )
        if part == "FORALL":
            inside = formula_holder.pop()
            var_name = formula_input[p + 1]

            if var_name not in var_count:
                var_count[var_name] = 1

            formula_holder.append(
                Unary(inside, Quantifier.UNIVERSAL, False, var_name)
            )
        if part == "EXIST":
            inside = formula_holder.pop()
            var_name = formula_input[p + 1]

            if var_name not in var_count:
                var_count[var_name] = 1

            formula_holder.append(
                Unary(inside, Quantifier.EXISTENTIAL, False, var_name)
            )
        if part == "done":
            break

    formula = formula_holder.pop()
    formula.set_var_count(var_count)
    return formula


def resolve(prover: ResolutionProver):
    print("Resolving ...")
    prover.apply_resolution()
    pass


def preprocess(preprocessor: PreProcessor) -> PreProcessor:
    print("Preprocessing ...")
    print("Executing Step 1. Negate conclusion")
    preprocessor.negate_conclusion()
    print("Step 1 completed")
    preprocessor.print_argument()
    print("")

    print("Executing Step 2. Turning arguments into ∃-free Prenex Normal Form")
    preprocessor.normalize_to_prenex()
    print("Step 2 completed")
    preprocessor.print_argument()
    print("")

    print("Executing Step 3. Getting clauses from Prenex Normal Form")
    clauses = preprocessor.convert_to_clauses()
    print("Step 3 completed")
    preprocessor.print_clauses()
    print("")

    shared.set_arg(preprocessor.get_arg())
    shared.set_premises(preprocessor.get_premises())
    shared.set_negated_conclusion(preprocessor.get_negated_conclusion()[0])
    shared.set_clauses(clauses)

    print("Preprocessing finished!")

    return preprocessor


def process_commands(cmd: str, user_input: []):
    if cmd == "input":
        if len(user_input) > 0:
            arg = shared.get_arg()
            arg.append(
                input_formula(input_list)
            )
            shared.set_arg(arg)
        else:
            raise Exception("No input")
    if cmd == "complete":
        shared.set_input_complete(True)
    if cmd == "print":
        shared.print_arg()
    if cmd == "preprocess":
        preprocess(
            PreProcessor(shared.get_arg())
        )
    if cmd == "resolve":
        resolve(
            ResolutionProver(
                shared.get_clauses(),
                shared.get_negated_conclusion()[0]
            )
        )


def execute_shunting_yard(tokens: List[str]):
    postfix_queue = []
    operator_stack = []

    for t, token in enumerate(tokens):
        if token == "FORM":
            function = [token, tokens[t + 1], tokens[t + 2]]
            postfix_queue.insert(0, function)
        if token == "FORALL" or token == "EXIST":
            quantifier = [token, tokens[t + 1]]
            operator_stack.append(quantifier)
        if token == "->" or token == "<->" or token == "AND" or token == "OR" or token == "NOT":
            operator_stack.append(token)
        if token == ")":
            operator = operator_stack.pop()
            postfix_queue.insert(0, operator)
        print("stack", operator_stack)
        print("queue", postfix_queue)

    while operator_stack:
        postfix_queue.insert(0, operator_stack.pop())
    postfix_queue.reverse()

    postfix_string = []
    for item in postfix_queue:
        if isinstance(item, list):
            postfix_string.append(' '.join(item))
        else:
            postfix_string.append(item)
    print(postfix_string)


# x F(x) H(x) ¬ G(x) ∧ ⇒ ∀
# FORM H x FORM F x NOT FORM G x AND -> FORALL x
# FORM F x FORM H x FORM G x AND NOT -> FORALL x
shared = Shared()
for line in fileinput.input(files='/Users/Kevin/Projects/proofster-prototype/test2.txt'):
    input_list = line.split()
    command = input_list.pop(0)
    process_commands(command, input_list)

infix = "( ( ( FORM A x AND FORM B x ) OR ( FORM C x AND FORM D x ) ) OR ( ( FORM E x AND FORM F x ) OR ( FORM G x AND FORM H x ) ) )".split()
execute_shunting_yard(infix)
