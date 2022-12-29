import fileinput
from enums import Connective, Quantifier
from formula import Unary, Binary, Variable, Function, Formula
from prover import ResolutionProver


def input_formula(formulaInput: [Formula]) -> Formula:
    formula_holder = []
    var_count = {}

    for index, part in enumerate(formulaInput):
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
            func_name = input_list[index + 1]
            var_name = input_list[index + 2]

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
            var_name = input_list[index + 1]

            if var_name not in var_count:
                var_count[var_name] = 1

            formula_holder.append(
                Unary(inside, Quantifier.UNIVERSAL, False, var_name)
            )
        if part == "EXIST":
            inside = formula_holder.pop()
            var_name = input_list[index + 1]

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


def input_commands(command_input: [], args: [Formula]):
    for part in command_input:
        if part == "print":
            print("Printing argument")
            for arg in args:
                arg.print_formula()
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
for line in fileinput.input(files='test2.txt'):
    input_list = line.split()
    label = input_list[0]
    input_list.pop(0)
    if label == "input":
        argument.append(
            input_formula(input_list)
        )
    if label == "command":
        input_commands(input_list, argument)
