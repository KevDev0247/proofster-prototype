from formula import Formula


class ResolutionProver:
    def __init__(self, premises: [Formula], negated_conclusion: [Formula]):
        self._premises = premises
        self._negated_conclusion = negated_conclusion

    def check_resolvable(self):
        # check if function name is the same
        # check if one is negated
        # check if it's the same after assignment
        pass

    def get_most_common_var(self):
        pass

    def resolve(self, clauses):
        pass
