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

from oqd_compiler_infrastructure.base import PassBase
from oqd_compiler_infrastructure.rule import ConversionRule

########################################################################################

__all__ = [
    "WalkBase",
    "Pre",
    "Post",
    "Level",
    "In",
]

########################################################################################


class WalkBase(PassBase):
    """
    This class represents a tree traversal algorithm to walk through an AST.

    Acknowledgement:
        This code was inspired by [SymbolicUtils.jl](https://github.com/JuliaSymbolics/SymbolicUtils.jl/blob/master/src/rewriters.jl#L167), [Liang.jl](https://github.com/Roger-luo/Liang.jl/blob/main/src/rewrite/walk.jl#L1)
    """

    def __init__(self, rule: PassBase, *, reverse: bool = False):
        super().__init__()

        self.rule = rule
        self.reverse = reverse

    @staticmethod
    def controlled_reverse(iterable, reverse, *, restore_type=False):
        new_iterable = reversed(iterable) if reverse else iterable
        new_iterable = (
            iterable.__class__(new_iterable) if restore_type else new_iterable
        )
        return new_iterable

    @property
    def children(self):
        return [self.rule]

    def map(self, model, **kwargs):
        return self.walk(model, **kwargs)

    def walk(self, model, **kwargs):
        for cls in model.__class__.__mro__:
            walk_func = getattr(self, "walk_{}".format(cls.__name__), None)
            if walk_func:
                break

        if not walk_func:
            walk_func = self.generic_walk

        return walk_func(model, **kwargs)

    def generic_walk(self, model, **kwargs):
        return self.rule(model, **kwargs)


########################################################################################


class Pre(WalkBase):
    """
    This class represents the pre order tree traversal algorithm that walks through an AST
    and applies the rule from top to bottom.

    Acknowledgement:
        This code was inspired by [SymbolicUtils.jl](https://github.com/JuliaSymbolics/SymbolicUtils.jl/blob/master/src/rewriters.jl#L187), [Liang.jl](https://github.com/Roger-luo/Liang.jl/blob/main/src/rewrite/walk.jl#L3)
    """

    def walk_dict(self, model, **kwargs):
        new_model = self.rule(model, **kwargs)

        new_model = {
            k: self.walk(v, **kwargs)
            for k, v in self.controlled_reverse(new_model.items(), self.reverse)
        }

        return {
            k: v for k, v in self.controlled_reverse(new_model.items(), self.reverse)
        }

    def walk_list(self, model, **kwargs):
        new_model = self.rule(model, **kwargs)

        new_model = [
            self.walk(e, **kwargs)
            for e in self.controlled_reverse(new_model, self.reverse)
        ]

        return self.controlled_reverse(new_model, self.reverse, restore_type=True)

    def walk_tuple(self, model, **kwargs):
        new_model = self.rule(model, **kwargs)

        new_model = tuple(
            [
                self.walk(e, **kwargs)
                for e in self.controlled_reverse(new_model, self.reverse)
            ]
        )

        return self.controlled_reverse(new_model, self.reverse, restore_type=True)

    def walk_VisitableBaseModel(self, model, **kwargs):
        new_model = self.rule(model, **kwargs)

        new_fields = {}
        for key in self.controlled_reverse(
            new_model.__class__.model_fields.keys(), self.reverse
        ):
            if key == "class_":
                continue
            new_fields[key] = self.walk(getattr(new_model, key), **kwargs)
        new_model = new_model.__class__(**new_fields)

        return new_model

    def walk_AST(self, model, **kwargs):
        new_model = self.rule(model, **kwargs)

        new_fields = {}
        for key in self.controlled_reverse(new_model.__class__._fields, self.reverse):
            new_fields[key] = self.walk(getattr(new_model, key), **kwargs)
        new_model = new_model.__class__(**new_fields)

        return new_model


class Post(WalkBase):
    """
    This class represents the post order tree traversal algorithm that walks through an AST
    and applies the rule from bottom to top.

    Acknowledgement:
        This code was inspired by [SymbolicUtils.jl](https://github.com/JuliaSymbolics/SymbolicUtils.jl/blob/master/src/rewriters.jl#L183), [Liang.jl](https://github.com/Roger-luo/Liang.jl/blob/main/src/rewrite/walk.jl#L9)
    """

    def walk_dict(self, model, **kwargs):
        new_model = {
            k: self.walk(v, **kwargs)
            for k, v in self.controlled_reverse(model.items(), self.reverse)
        }
        new_model = {
            k: v for k, v in self.controlled_reverse(new_model.items(), self.reverse)
        }

        if isinstance(self.rule, ConversionRule):
            self.rule._operands = new_model
            new_model = self.rule(model, **kwargs)
        else:
            new_model = self.rule(new_model, **kwargs)

        return new_model

    def walk_list(self, model, **kwargs):
        new_model = [
            self.walk(e, **kwargs) for e in self.controlled_reverse(model, self.reverse)
        ]
        new_model = self.controlled_reverse(new_model, self.reverse, restore_type=True)

        if isinstance(self.rule, ConversionRule):
            self.rule._operands = new_model
            new_model = self.rule(model, **kwargs)
        else:
            new_model = self.rule(new_model, **kwargs)

        return new_model

    def walk_tuple(self, model, **kwargs):
        new_model = tuple(
            [
                self.walk(e, **kwargs)
                for e in self.controlled_reverse(model, self.reverse)
            ]
        )
        new_model = self.controlled_reverse(new_model, self.reverse, restore_type=True)

        if isinstance(self.rule, ConversionRule):
            self.rule._operands = new_model
            new_model = self.rule(model, **kwargs)
        else:
            new_model = self.rule(new_model, **kwargs)

        return new_model

    def walk_VisitableBaseModel(self, model, **kwargs):
        new_fields = {}
        for key in self.controlled_reverse(
            model.__class__.model_fields.keys(), self.reverse
        ):
            if key == "class_":
                continue
            new_fields[key] = self.walk(getattr(model, key), **kwargs)

        if isinstance(self.rule, ConversionRule):
            self.rule._operands = new_fields
            new_model = self.rule(model, **kwargs)
        else:
            new_model = model.__class__(**new_fields)
            new_model = self.rule(new_model, **kwargs)

        return new_model

    def walk_AST(self, model, **kwargs):
        new_fields = {}
        for key in self.controlled_reverse(model.__class__._fields, self.reverse):
            new_fields[key] = self.walk(getattr(model, key), **kwargs)

        if isinstance(self.rule, ConversionRule):
            self.rule._operands = new_fields
            new_model = self.rule(model, **kwargs)
        else:
            new_model = model.__class__(**new_fields)
            new_model = self.rule(new_model, **kwargs)

        return new_model


class Level(WalkBase):
    """
    This class represents the level/breadth first order tree traversal algorithm that walks through an AST.
    """

    def __init__(self, rule, *, reverse=False):
        super().__init__(rule, reverse=reverse)

        self.stack = []
        self.initial = True

    def generic_walk(self, model, **kwargs):
        if self.initial:
            self.stack.append(model)
            self.initial = False

        self.rule(self.stack.pop(0), **kwargs)
        if self.stack:
            self.walk(self.stack[0], **kwargs)
        return model

    def walk_list(self, model, **kwargs):
        if self.initial:
            self.stack.append(model)
            self.initial = False

        self.stack.extend(self.controlled_reverse(model, self.reverse))

        self.rule(self.stack.pop(0), **kwargs)
        if self.stack:
            self.walk(self.stack[0], **kwargs)
        return model

    def walk_tuple(self, model, **kwargs):
        if self.initial:
            self.stack.append(model)
            self.initial = False

        self.stack.extend(self.controlled_reverse(model, self.reverse))

        self.rule(self.stack.pop(0), **kwargs)
        if self.stack:
            self.walk(self.stack[0], **kwargs)
        return model

    def walk_dict(self, model, **kwargs):
        if self.initial:
            self.stack.append(model)
            self.initial = False

        self.stack.extend(self.controlled_reverse(model.values(), self.reverse))

        self.rule(self.stack.pop(0), **kwargs)
        if self.stack:
            self.walk(self.stack[0], **kwargs)
        return model

    def walk_VisitableBaseModel(self, model, **kwargs):
        if self.initial:
            self.stack.append(model)
            self.initial = False

        self.stack.extend(
            self.controlled_reverse(
                [
                    getattr(model, k)
                    for k in model.__class__.model_fields.keys()
                    if k != "class_"
                ],
                self.reverse,
            )
        )

        self.rule(self.stack.pop(0), **kwargs)
        if self.stack:
            self.walk(self.stack[0], **kwargs)
        return model

    def walk_AST(self, model, **kwargs):
        if self.initial:
            self.stack.append(model)
            self.initial = False

        self.stack.extend(
            self.controlled_reverse(
                [getattr(model, k) for k in model.__class__._fields if k != "class_"],
                self.reverse,
            )
        )

        self.rule(self.stack.pop(0), **kwargs)
        if self.stack:
            self.walk(self.stack[0], **kwargs)
        return model


class In(WalkBase):
    """
    This class represents the in order tree traversal algorithm that walks through an AST.
    """

    def generic_walk(self, model, **kwargs):
        self.rule(model, **kwargs)
        return model

    def walk_list(self, model, **kwargs):
        for e in self.controlled_reverse(model, self.reverse, restore_type=True)[:-1]:
            self.walk(e, **kwargs)

        self.rule(model, **kwargs)
        if model:
            self.walk(
                self.controlled_reverse(model, self.reverse, restore_type=True)[-1],
                **kwargs,
            )
        return model

    def walk_tuple(self, model, **kwargs):
        for e in self.controlled_reverse(model, self.reverse, restore_type=True)[:-1]:
            self.walk(e, **kwargs)

        self.rule(model, **kwargs)
        if model:
            self.walk(
                self.controlled_reverse(model, self.reverse, restore_type=True)[-1],
                **kwargs,
            )
        return model

    def walk_dict(self, model, **kwargs):
        for v in list(self.controlled_reverse(model.values(), self.reverse))[:-1]:
            self.walk(v, **kwargs)

        self.rule(model, **kwargs)
        if model:
            self.walk(
                list(self.controlled_reverse(model.values(), self.reverse))[-1],
                **kwargs,
            )
        return model

    def walk_VisitableBaseModel(self, model, **kwargs):
        keys = [k for k in model.__class__.model_fields.keys() if k != "class_"]
        keys = self.controlled_reverse(keys, self.reverse, restore_type=True)
        for k in keys[:-1]:
            self.walk(getattr(model, k), **kwargs)

        self.rule(model, **kwargs)
        if keys:
            self.walk(getattr(model, keys[-1]), **kwargs)
        return model

    def walk_AST(self, model, **kwargs):
        keys = [k for k in model.__class__._fields if k != "class_"]
        keys = self.controlled_reverse(keys, self.reverse, restore_type=True)
        for k in keys[:-1]:
            self.walk(getattr(model, k), **kwargs)

        self.rule(model, **kwargs)
        if keys:
            self.walk(getattr(model, keys[-1]), **kwargs)
        return model
