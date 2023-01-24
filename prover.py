from enums import Type
from formula import Formula, Function, Variable


def is_assignable(target: Formula, assignment: Formula):
    inside_type = target.get_inside().get_formula_type()
    if ((not target.get_assigned()) or
            (inside_type == Type.FUNCTION and
             assignment.get_formula_type() == Type.FUNCTION)):
        return False
    return True


def assign_var(clause: [Formula], to_assign: Formula, assignment: Formula) -> [Formula]:
    # need to make copy ctor
    to_assign_var = to_assign.get_inside().get_var_name()
    for atom in clause:
        inside = atom.get_inside()
        if inside.get_formula_type() != Type.VARIABLE:
            if inside.get_inside().get_var_name() == to_assign_var:
                inside.set_inside(
                    Variable(assignment.get_inside().get_var_name())
                )
        else:
            # atom and to assign are pointing at the same thing
            if inside.get_var_name() == to_assign_var:
                atom.set_inside(
                    Variable(assignment.get_inside().get_var_name())
                )
    return clause


def assign_func(clause: [Formula], to_assign: Formula, assignment: Formula):
    for atom in clause:
        inside = atom.get_inside()
        if inside.get_var_name() == to_assign.get_var_name():
            atom.set_inside(
                Variable(assignment.get_inside().get_var_name())
            )
    return clause


def assign(clause: [Formula], to_assign: Formula, assignment: Formula):
    # need copy ctor
    inside_type = assignment.get_inside().get_formula_type()
    origin = to_assign
    if inside_type == Type.VARIABLE:
        assign_var(
            clause, to_assign,
            assignment
        )
    else:
        assign_func(
            clause, to_assign,
            assignment
        )
    print("Assignment Step")
    print("Assigned ", end="")
    assignment.print_formula()
    print(" to ", end="")
    origin.print_formula()
    print("")


def print_clauses(clauses):
    for c, clause in enumerate(clauses):
        for f, formula in enumerate(clause):
            formula.print_formula()
            if f < len(clause) - 1:
                print(" ∨ ", end="")
        if c < len(clauses) - 1:
            print(", ", end="")


class ResolutionProver:
    def __init__(self, clauses: [Formula], negated_conclusion: [Formula]):
        self._clauses = clauses
        self._support = [negated_conclusion]

    def is_in_support(self, to_check: Formula):
        for clause in self._support:
            if to_check in clause:
                return True
        return False

    # bug
    # Resolved
    # F(u) and G(f(x1)) ¬F(u) G(u)
    # Resolvent
    # G(f(x1))

    def resolve(self, to_resolve: Formula):
        for c, clause in enumerate(self._clauses):
            for a, atom in enumerate(clause):
                if (to_resolve.get_func_name() == atom.get_func_name() and
                        to_resolve.get_negation() != atom.get_negation() and
                        is_assignable(atom, to_resolve)):
                    # perform assignment and resolve
                    unresolved = self._clauses[c].copy()
                    assign(self._clauses[c], atom, to_resolve)
                    self._clauses[c].pop(a)

                    # adding resolvent to set of support
                    resolvent = self._clauses[c].copy()
                    for t, to_check in enumerate(resolvent):
                        if self.is_in_support(to_check):
                            resolvent.pop(t)
                    self._support.append(resolvent)

                    # print something
                    print("Resolution Step")
                    print("Resolved ", end="")
                    to_resolve.print_formula()
                    print(" and ", end="")
                    for f, final in enumerate(unresolved):
                        final.print_formula()
                        print(" ", end="")
                    print("")

                    print("Resolvent ", end="")
                    for f, final in enumerate(resolvent):
                        final.print_formula()
                        print(" ", end="")
                    print("")

        #             return True
        # return False

    def apply_resolution(self):
        while self._support:
            clause = self._support.pop()
            if not clause:
                print("resolved")
                break
            for atom in clause:
                self.resolve(atom)
