# Copyright 2024-2025 Open Quantum Design

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import ast

from oqd_compiler_infrastructure.base import PassBase
from oqd_compiler_infrastructure.interface import VisitableBaseModel

########################################################################################

__all__ = [
    "RewriterBase",
    "Chain",
    "FixedPoint",
]

########################################################################################


class RewriterBase(PassBase):
    """
    This class represents a wrapper for passes to compose and modify their logic without
    affecting the internals of a pass.

    Acknowledgement:
        This code was inspired by [SynbolicUtils.jl](https://github.com/JuliaSymbolics/SymbolicUtils.jl/blob/master/src/rewriters.jl), [Liang.jl](https://github.com/Roger-luo/Liang.jl/tree/main/src/rewrite).
    """

    pass


########################################################################################


class Chain(RewriterBase):
    """
    This class represents a composite pass where the passes are applied sequentially.

    Acknowledgement:
        This code was inspired by [SymbolicUtils.jl](https://github.com/JuliaSymbolics/SymbolicUtils.jl/blob/master/src/rewriters.jl#L64C8-L64C13), [Liang.jl](https://github.com/Roger-luo/Liang.jl/blob/main/src/rewrite/chain.jl).
    """

    def __init__(self, *rules):
        super().__init__()

        self.rules = list(rules)
        pass

    @property
    def children(self):
        return self.rules

    def map(self, model):
        new_model = model
        for rule in self.rules:
            new_model = rule(new_model)
        return new_model


class FixedPoint(RewriterBase):
    """
    This class represents a wrapped pass that is applied until the object/IR converges to a fixed point
    or reaches a maximum iteration count.

    Acknowledgement:
        This code was inspired by [SymbolicUtils.jl](https://github.com/JuliaSymbolics/SymbolicUtils.jl/blob/master/src/rewriters.jl#L117C8-L117C16), [Liang.jl](https://github.com/Roger-luo/Liang.jl/blob/main/src/rewrite/fixpoint.jl).
    """

    @classmethod
    def _default_eq(cls, model1, model2):
        if type(model1) is not type(model2):
            return False

        if isinstance(model1, ast.AST):
            for k in model1.__class__._fields:
                if k in ("lineno", "col_offset"):
                    continue

                if not cls._default_eq(getattr(model1, k), getattr(model2, k)):
                    return False

            return True

        if isinstance(model1, VisitableBaseModel):
            for k in model1.__class__.model_fields.keys():
                if not cls._default_eq(getattr(model1, k), getattr(model2, k)):
                    return False

            return True

        if isinstance(model1, (list, tuple)):
            for pairs in zip(model1, model2):
                if not cls._default_eq(*pairs):
                    return False

            return True

        if isinstance(model1, dict):
            keys = set(model1.keys()).union(model2.keys())

            if keys != set(model1.keys()) or keys != set(model2.keys()):
                return False

            for k in keys:
                if not cls._default_eq(model1.get(k), model2.get(k)):
                    return False

            return True

        return model1 == model2

    def __init__(self, rule, *, max_iter=1000, equality=None):
        super().__init__()

        self.rule = rule
        self.max_iter = max_iter
        self.equality = equality if equality else self._default_eq

    @property
    def children(self):
        return [self.rule]

    def map(self, model):
        i = 0
        new_model = model
        while True:
            _model = self.rule(new_model)

            if self.equality(_model, new_model) or i >= self.max_iter:
                return new_model

            new_model = _model
            i += 1
