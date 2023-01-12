from formula import Formula


def check_resolvable(target: Formula, clauses: [Formula]):
    # check if function name is the same
    # check if one is negated
    # check if it's the same after assignment (for multiple vars)
    for c, clause in enumerate(clauses):
        if (target.get_func_name() == clause.get_func_name() and
                target.get_negation() != clause.get_negation()):
            return True
    return False


class ResolutionProver:
    def __init__(self, premises: [Formula], negated_conclusion: [Formula]):
        self._premises = premises
        self._negated_conclusion = negated_conclusion
        self._support = [negated_conclusion]

    def get_most_common_var(self):
        pass

    def resolve(self):
        pass
