# Copyright 2024 Open Quantum Design

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from oqd_compiler_infrastructure.base import PassBase

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

    def __init__(self, rule, *, max_iter=1000):
        super().__init__()

        self.rule = rule
        self.max_iter = max_iter
        pass

    @property
    def children(self):
        return [self.rule]

    def map(self, model):
        i = 0
        new_model = model
        while True:
            _model = self.rule(new_model)

            if _model == new_model or i >= self.max_iter:
                return new_model

            new_model = _model
            i += 1
