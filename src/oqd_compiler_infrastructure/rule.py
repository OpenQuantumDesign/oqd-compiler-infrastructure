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
    "RuleBase",
    "RewriteRule",
    "ConversionRule",
    "PrettyPrint",
]


########################################################################################


class RuleBase(PassBase):
    """
    This class represents a rule applied to an IR.
    """

    @property
    def children(self):
        return []


class RewriteRule(RuleBase):
    """
    This class represents a rule used to rewrite a type or IR. The result of the same type
    or IR.

    Acknowledgement:
        This code was inspired by [MLIR](https://github.com/llvm/llvm-project/blob/main/mlir/include/mlir/IR/PatternMatch.h#L246), [Bloqade-python](https://github.com/QuEraComputing/bloqade-python/blob/main/src/bloqade/ir/visitor.py#L34)
    """

    def map(self, model):
        for cls in model.__class__.__mro__:
            map_func = getattr(self, "map_{}".format(cls.__name__), None)
            if map_func:
                break

        if not map_func:
            map_func = self.generic_map

        return map_func(model)

    def generic_map(self, model):
        return model

    pass


class ConversionRule(RuleBase):
    """
    This class represents a rule used to convert between different types and IRs.

    Acknowledgement:
        This code was inspired by [MLIR]()
    """

    def __init__(self):
        super().__init__()
        self.operands = None

    def map(self, model):
        operands = self.operands

        for cls in model.__class__.__mro__:
            map_func = getattr(self, "map_{}".format(cls.__name__), None)
            if map_func:
                break

        if not map_func:
            map_func = self.generic_map

        return map_func(model, operands=operands)

    def generic_map(self, model, operands):
        return model


########################################################################################


class PrettyPrint(ConversionRule):
    """
    This class represents a rewrite rule that constructs a string to represent an AST.
    """

    def __init__(self, *, indent="  "):
        super().__init__()

        self.indent = indent

    def generic_map(self, model, operands):
        return f"{model.__class__.__name__}({model})"

    def map_list(self, model, operands):
        s = f"{model.__class__.__name__}"

        _s = ""
        for n, o in enumerate(operands):
            _s += f"\n{self.indent}- {n}: " + f"\n{self.indent}".join(o.split("\n"))

        s = s + _s

        return s

    def map_tuple(self, model, operands):
        s = f"{model.__class__.__name__}"

        _s = ""
        for n, o in enumerate(operands):
            _s += f"\n{self.indent}- {n}: " + f"\n{self.indent}".join(o.split("\n"))

        s = s + _s

        return s

    def map_dict(self, model, operands):
        s = f"{model.__class__.__name__}"

        _s = ""
        for k, v in operands.items():
            _s += f"\n{self.indent}- {k}: " + f"\n{self.indent}".join(v.split("\n"))

        s = s + _s

        return s

    def map_VisitableBaseModel(self, model, operands):
        s = f"{model.__class__.__name__}"

        _s = ""
        for k, v in operands.items():
            _s += f"\n{self.indent}- {k}: " + f"\n{self.indent}".join(v.split("\n"))

        s = s + _s

        return s
