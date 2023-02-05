import json
from abc import ABC, abstractmethod
from typing import Dict, List, Tuple
from enums import Connective, Type, Quantifier


class Formula(ABC):
    def __init__(
            self,
            formula_type: Type,
            var_count=None,
            quant_list=None
    ):
        if var_count is None:
            var_count = {}
        if quant_list is None:
            quant_list = []
        self._formula_type = formula_type
        self._var_count = var_count
        self._quant_list = quant_list

    def print_json(self):
        print(self.to_json())

    def print_formula(self):
        print(self.to_string(), end="")

    @abstractmethod
    def to_json(self) -> json:
        pass

    @abstractmethod
    def from_json(self, json_data) -> 'Formula':
        pass

    @abstractmethod
    def to_string(self) -> str:
        pass

    @abstractmethod
    def set_var(self, var: str):
        pass

    @abstractmethod
    def set_var_count(self, var_count: Dict):
        pass

    def set_quant_list(self, quant_list: List[Tuple[Quantifier, str]]):
        self._quant_list = quant_list

    def get_formula_type(self) -> Type:
        return self._formula_type

    def get_var_count(self) -> Dict:
        return self._var_count

    def get_quant_list(self) -> List[Tuple[Quantifier, str]]:
        return self._quant_list


class Binary(Formula):

    def __init__(
            self,
            left: Formula,
            right: Formula,
            connective: Connective,
            is_clause=False,
            var_count=None,
            quant_list=None
    ):
        super().__init__(
            Type.BINARY,
            var_count,
            quant_list
        )
        self._left = left
        self._connective = connective
        self._right = right
        self._is_clause = is_clause

    def to_json(self) -> json:
        return {
            'left': self._left.to_json(),
            'right': self._right.to_json(),
            'connective': self._connective,
            'is_clause': self._is_clause,
            'var_count': self._var_count,
            'quant_list': self._quant_list
        }

    def from_json(self, json_data) -> Formula:
        left = self._left.from_json(json_data['left'])
        right = self._right.from_json(json_data['right'])
        connective = Connective(json_data['connective'])
        is_clause = json_data['is_clause']
        var_count = json_data['var_count']
        quant_list = json_data['quant_list']

        return Binary(
            left,
            right,
            connective,
            is_clause,
            var_count,
            quant_list
        )

    def to_string(self) -> str:
        result = "(" + self._left.to_string()
        if self._connective == Connective.IMPLICATION:
            result += " ⇒ "
        if self._connective == Connective.BICONDITIONAL:
            result += " ⇔ "
        if self._connective == Connective.AND:
            result += " ∧ "
        if self._connective == Connective.OR:
            result += " ∨ "
        result += self._right.to_string()
        result += ")"
        return result

    def get_left(self) -> Formula:
        return self._left

    def get_connective(self) -> Connective:
        return self._connective

    def get_right(self) -> Formula:
        return self._right

    def get_is_clause(self) -> bool:
        return self._is_clause

    def set_var(self, var: str):
        self._left.set_var(var)
        self._right.set_var(var)

    def set_var_count(self, var_count: Dict):
        self._var_count = var_count
        self._left.set_var_count(var_count)
        self._right.set_var_count(var_count)

    def set_left(self, left: Formula):
        self._left = left

    def set_connective(self, connective: Connective):
        self._connective = connective

    def set_right(self, right: Formula):
        self._right = right

    def set_is_clause(self, is_clause: bool):
        self._is_clause = is_clause


class Unary(Formula):
    def __init__(
            self,
            inside: Formula,
            quantifier: Quantifier,
            negation: bool,
            quant_var: str,
            var_count=None,
            quant_list=None
    ):
        super().__init__(
            Type.UNARY,
            var_count,
            quant_list
        )
        self._inside = inside
        self._quantifier = quantifier
        self._negation = negation
        self._quant_var = quant_var

    def to_json(self) -> json:
        return {
            'inside': self._inside.to_json(),
            'quantifier': self._quantifier,
            'negation': self._negation,
            'quant_var': self._quant_var,
            'var_count': self._var_count,
            'quant_list': self._quant_list
        }

    def from_json(self, json_data) -> Formula:
        inside = self._inside.to_json()
        quantifier = self._quantifier
        negation = self._negation
        quant_var = self._quant_var
        var_count = json_data['var_count']
        quant_list = json_data['quant_list']

        return Unary(
            inside,
            quantifier,
            negation,
            quant_var,
            var_count,
            quant_list
        )

    def to_string(self) -> str:
        result = ""
        if self._negation:
            result += "¬"
        if self._quantifier == Quantifier.EXISTENTIAL:
            result += "∃"
        if self._quantifier == Quantifier.UNIVERSAL:
            result += "∀"
        result += self._inside.to_string()
        return result

    def get_quantifier(self) -> Quantifier:
        return self._quantifier

    def get_inside(self) -> Formula:
        return self._inside

    def get_quant_var(self) -> str:
        return self._quant_var

    def get_negation(self):
        return self._negation

    def set_var(self, var: str):
        self._inside.set_var(var)

    def set_var_count(self, var_count: Dict):
        self._var_count = var_count
        self._inside.set_var_count(var_count)

    def set_quantifier(self, quantifier: Quantifier):
        self._quantifier = quantifier

    def set_inside(self, inside: Formula):
        self._inside = inside

    def set_quant_var(self, quant_var: str):
        self._quant_var = quant_var

    def set_negation(self, negation: bool):
        self._negation = negation


class Variable(Formula):
    def __init__(
            self,
            var_name,
            var_count=None,
            quant_list=None
    ):
        super().__init__(
            Type.VARIABLE,
            var_count,
            quant_list
        )
        self._var_name = var_name

    def to_json(self) -> json:
        return {
            'var_name': self._var_name,
            'var_count': self._var_count,
            'quant_list': self._quant_list
        }

    def from_json(self, json_data) -> Formula:
        var_name = self._var_name
        var_count = json_data['var_count']
        quant_list = json_data['quant_list']

        return Variable(
            var_name,
            var_count,
            quant_list
        )

    def to_string(self) -> str:
        return self._var_name

    def get_var_name(self) -> str:
        return self._var_name

    def set_var(self, var_name):
        self._var_name = var_name

    def set_var_count(self, var_count: Dict):
        self._var_count = var_count


class Function(Formula):
    def __init__(
            self,
            func_name: str,
            inside: Formula,
            negation=False,
            assigned=True,
            var_count=None,
            quant_list=None
    ):
        super().__init__(
            Type.FUNCTION,
            var_count,
            quant_list
        )
        self._func_name = func_name
        self._inside = inside
        self._negation = negation
        self._assigned = assigned

    def to_json(self) -> json:
        return {
            'func_name': self._func_name,
            'inside': self._inside.to_json(),
            'negation': self._negation,
            'assigned': self._assigned,
            'var_count': self._var_count,
            'quant_list': self._quant_list
        }

    def from_json(self, json_data) -> Formula:
        func_name = self._func_name
        inside = self._inside.to_json()
        negation = self._negation
        assigned = self._assigned
        var_count = json_data['var_count']
        quant_list = json_data['quant_list']

        return Function(
            func_name,
            inside,
            negation,
            assigned,
            var_count,
            quant_list
        )

    def to_string(self) -> str:
        result = ""
        if self._negation:
            result += "¬"
        result += self._func_name
        result += "("
        result += self._inside.to_string()
        result += ")"
        return result

    def get_func_name(self) -> str:
        return self._func_name

    def get_inside(self) -> Formula:
        return self._inside

    def get_negation(self) -> bool:
        return self._negation

    def get_assigned(self) -> bool:
        return self._assigned

    def set_var_count(self, var_count: Dict):
        self._var_count = var_count
        self._inside.set_var_count(var_count)

    def set_var(self, var):
        self._inside.set_var(var)

    def set_inside(self, inside: Formula):
        self._inside = inside

    def set_negation(self, negation: bool):
        self._negation = negation

    def set_assigned(self, assigned: bool):
        self._assigned = assigned
