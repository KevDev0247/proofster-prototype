from enums import Type
from formula import Formula, Function


def check_assignable(clauses: [Formula]):
    for clause in clauses:
        inside_type = clause.get_inside().get_formula_type()
        if not clause.get_assignable() or inside_type == Type.FUNCTION:
            return False
    return True


class ResolutionProver:
    def __init__(self, clauses: [Formula], negated_conclusion: [Formula]):
        self._clauses = clauses
        self._support = [negated_conclusion]

    # need a guard
    def assign_var(self, to_assign: str, var: str):
        for clause in self._clauses:
            for atom in clause:
                if atom.get_inside().get_formula_type() != Type.VARIABLE:
                    if atom.get_inside().get_inside().get_var_name() == to_assign:
                        atom.get_inside().get_inside().set_var(var)
                else:
                    if atom.get_inside().get_var_name() == to_assign:
                        atom.get_inside().set_var(var)

    def assign_func(self, to_assign: str, func: Function):
        pass

    def check_resolvable(self, target: Formula):
        # check if function name is the same
        # check if one is negated
        # check if already assigned
        # check if it's the same after assignment (for multiple vars)
        for clause in self._clauses:
            for atom in clause:
                if (target.get_func_name() == atom.get_func_name() and
                        target.get_negation() != atom.get_negation()):
                    return True
        return False

    def get_most_common_var(self):
        pass

    def resolve(self, target: Formula):
        pass

    def apply_resolution(self):
        for atom in self._support:
            pass
