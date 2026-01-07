from typing import Any, Dict, Optional
from .rule import ConversionRule
from pydantic import BaseModel

import ast

########################################################################################


def match(pattern, model):
    matcher = _Matcher(pattern=ast.parse(pattern))

    return matcher(model)


########################################################################################


class _Matcher(ConversionRule):
    def __init__(self, pattern: ast.AST):
        super().__init__()

        self.pattern = pattern

    @staticmethod
    def _reduce_pattern(pattern):
        while pattern and not isinstance(pattern, ast.Call):
            if isinstance(pattern, ast.Module):
                pattern = pattern.body[0]
                continue

            if isinstance(pattern, ast.Expr):
                pattern = pattern.value
                continue

            raise TypeError("Unsupported AST pattern")

        return pattern

    @property
    def pattern(self):
        return self._pattern

    @pattern.setter
    def pattern(self, value):
        self._pattern = self._reduce_pattern(value)

    def generic_map(self, model, operands):
        node_names = (
            {x.id for x in self.pattern.func.slice.elts}
            if isinstance(self.pattern.func, ast.Subscript)
            and isinstance(self.pattern.func.value, ast.Name)
            and self.pattern.func.value.id == ("Union")
            else {ast.unparse(self.pattern.func)}
        )

        pattern = self.pattern

        result = MatchResult(state=True, variables={})

        if node_names.intersection(map(lambda x: x.__name__, model.__class__.__mro__)):
            for a in pattern.args:
                if isinstance(a, ast.Name):
                    result.update({a.id: model})
                    continue
                raise TypeError(
                    f"Unsupported type ({a.__class__.__name__}) when matching args"
                )

            for k in pattern.keywords:
                if isinstance(k.value, ast.Call):
                    self.pattern = k.value
                    _result = self(getattr(model, k.arg))

                    result.add(_result)
                    continue

                if isinstance(k.value, ast.Constant) and k.value.value == Ellipsis:
                    continue

                if isinstance(k.value, ast.Name):
                    result.update({k.value.id: getattr(model, k.arg)})
                    continue

                raise TypeError(
                    f"Unsupported type ({k.value.__class__.__name__}) when matching keywords"
                )

            return result
        else:
            return MatchResult(state=False, variables=None)


########################################################################################


class MatchResult(BaseModel):
    state: bool
    variables: Optional[Dict[str, Any]]

    def __bool__(self):
        return self.state

    def add(self, other):
        if not isinstance(other, MatchResult):
            raise TypeError("Unsupported addition of MatchResult and other type.")

        state = self.state and other.state
        self.state = state

        if state:
            variables = dict(**self.variables, **other.variables)
            self.update(variables)

        return MatchResult(state=state, variables=variables if state else None)

    def update(self, variables):
        self.variables.update(variables)

    def __getitem__(self, key):
        return self.variables[key]
