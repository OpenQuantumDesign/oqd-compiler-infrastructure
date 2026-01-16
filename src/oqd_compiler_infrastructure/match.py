import copy
from typing import Any, Dict, Optional

from .base import PassBase
from .rewriter import RewriterBase
from .rule import ConversionRule, RewriteRule
from pydantic import BaseModel

import ast


########################################################################################

__all__ = ["Match"]

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


########################################################################################


def _reduce_pattern(pattern):
    if isinstance(pattern, str):
        pattern = ast.parse(pattern)

    while pattern and not isinstance(pattern, ast.Call):
        if isinstance(pattern, ast.Module):
            pattern = pattern.body[0]
            continue

        if isinstance(pattern, ast.Expr):
            pattern = pattern.value
            continue

        raise TypeError("Unsupported AST pattern")

    return pattern


class _MatchPattern(ConversionRule):
    def __init__(self, pattern: ast.AST | str):
        super().__init__()

        self.pattern = pattern

    @property
    def pattern(self):
        return self._pattern

    @pattern.setter
    def pattern(self, value):
        self._pattern = _reduce_pattern(value)

    def map_dict(self, model, operands):
        return self.generic_map(model, operands)

    def map_list(self, model, operands):
        return self.generic_map(model, operands)

    def map_tuple(self, model, operands):
        return self.generic_map(model, operands)

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

                    match model:
                        case dict():
                            _result = self(model.get(k.arg))
                        case _:
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


class _MatchSubstitute(RewriteRule):
    def __init__(self, pattern: ast.AST | str, substitutions: Dict[str, Any]):
        super().__init__()

        self.pattern = pattern
        self.substitutions = substitutions

    @property
    def pattern(self):
        return self._pattern

    @pattern.setter
    def pattern(self, value):
        self._pattern = _reduce_pattern(value)

    def generic_map(self, model):
        node_names = (
            {x.id for x in self.pattern.func.slice.elts}
            if isinstance(self.pattern.func, ast.Subscript)
            and isinstance(self.pattern.func.value, ast.Name)
            and self.pattern.func.value.id == ("Union")
            else {ast.unparse(self.pattern.func)}
        )

        pattern = self.pattern

        if node_names.intersection(map(lambda x: x.__name__, model.__class__.__mro__)):
            if pattern.args and isinstance(pattern.args[0], ast.Name):
                return self.substitutions[pattern.args[0].id]

            if pattern.args:
                raise TypeError(
                    f"Unsupported type ({pattern.args.__class__.__name__}) when matching args"
                )

            new_model = copy.deepcopy(model)
            for k in pattern.keywords:
                if isinstance(k.value, (ast.Call, ast.Name)):
                    self.pattern = k.value

                    match new_model:
                        case dict():
                            new_model[k.arg] = self(model.get(k.arg))
                        case _:
                            setattr(new_model, k.arg, self(getattr(model, k.arg)))

                    continue

                if isinstance(k.value, ast.Constant) and k.value.value == Ellipsis:
                    continue

                raise TypeError(
                    f"Unsupported type ({k.value.__class__.__name__}) when matching keywords"
                )

            return new_model
        else:
            raise ValueError("Pattern does not match model")


########################################################################################


class Match(RewriterBase):
    def __init__(self, pattern: str, rule: PassBase, *, reuse=False):
        super().__init__()

        self._rule = rule
        self.pattern = pattern
        self.reuse = reuse

        self._rule_copies = []

    @property
    def rule(self):
        if self.reuse:
            return self._rule

        self._rule_copies.append(copy.deepcopy(self._rule))
        return self._rule_copies[-1]

    @property
    def children(self):
        if self.reuse:
            return [self._rule]

        return self._rule_copies

    def map(self, model):
        return self.match(model)

    def match(self, model):
        self.match_result = _MatchPattern(pattern=self.pattern)(model)

        if not self.match_result:
            return model

        substitutions = {
            k: self.rule(v) for k, v in self.match_result.variables.items()
        }

        return _MatchSubstitute(pattern=self.pattern, substitutions=substitutions)(
            model
        )
