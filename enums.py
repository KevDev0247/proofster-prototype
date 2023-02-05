from enum import IntEnum


class Quantifier(IntEnum):
    EXISTENTIAL = 1
    UNIVERSAL = 2
    NONE = 3


class Connective(IntEnum):
    IMPLICATION = 1
    BICONDITIONAL = 2
    AND = 3
    OR = 4


class Type(IntEnum):
    UNARY = 1
    BINARY = 2
    FUNCTION = 3
    VARIABLE = 4
