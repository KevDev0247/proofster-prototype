from enums import Type
from formula import Formula, Function, Variable


def is_assignable(target: Formula, assignment: Formula):
    inside_type = target.get_inside().get_formula_type()
    if ((not target.get_assigned()) or
            (inside_type == Type.FUNCTION and
             assignment.get_formula_type() == Type.FUNCTION)):
        return False
    return True


def assign_var(clause: [Formula], to_assign: str, assignment: Variable) -> [Formula]:
    for atom in clause:
        inside = atom.get_inside()
        if inside.get_formula_type() != Type.VARIABLE:
            if inside.get_inside().get_var_name() == to_assign:
                inside.set_inside(assignment)
        else:
            if inside.get_var_name() == to_assign:
                atom.set_inside(assignment)
    return clause


def assign_func(clause: [Formula], to_assign: str, assignment: Function):
    for atom in clause:
        inside = atom.get_inside()

        if inside.get_var_name() == to_assign:
            atom.set_inside(assignment)
    return clause


class ResolutionProver:
    def __init__(self, clauses: [Formula], negated_conclusion: Formula):
        self._clauses = clauses
        self._support = [negated_conclusion]

    # need a guard

    def resolve(self, assignment: Formula):
        # check if function name is the same
        # check if one is negated
        # check if it's assignable
        for clause in self._clauses:
            for atom in clause:
                if (assignment.get_func_name() == atom.get_func_name() and
                        assignment.get_negation() != atom.get_negation() and
                        is_assignable(atom, assignment)):
                    inside_type = assignment.get_inside().get_formula_type()
                    if inside_type == Type.VARIABLE:
                        assign_var(
                            clause, atom,
                            assignment.get_var_name()
                        )
                    else:
                        assign_func(
                            clause, atom,
                            assignment.get_var_name()
                        )
                    # print something
                    # continue resolving
                    # adding to set of support
                    return True
        return False

    def apply_resolution(self):
        # use recursion
        for atom in self._support:
            pass
