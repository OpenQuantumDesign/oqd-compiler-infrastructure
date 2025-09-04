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


import pytest
from oqd_compiler_infrastructure import (
    Post,
    ConversionRule,
    VisitableBaseModel,
)
from typing import Dict, List, Tuple

########################################################################################


class X(VisitableBaseModel):
    a: Dict[str, int]


class Y(VisitableBaseModel):
    a: List[int]


class Z(VisitableBaseModel):
    a: Tuple[int, int]


########################################################################################


class CustomRule(ConversionRule):
    def map_X(self, model, operands):
        if model.a == operands["a"]:
            raise ValueError("Conversion rule mutated attribute.")

    def map_Y(self, model, operands):
        if model.a == operands["a"]:
            raise ValueError("Conversion rule mutated attribute.")

    def map_Z(self, model, operands):
        if model.a == operands["a"]:
            raise ValueError("Conversion rule mutated attribute.")

    def map_int(self, model, operands):
        return model + 1


class CustomRule2(ConversionRule):
    def map_X(self, model, operands):
        if model.a == operands["a"]:
            raise ValueError("Conversion rule mutated model attribute.")
        return model.__class__(a=operands["a"])

    def map_Y(self, model, operands):
        if model.a == operands["a"]:
            raise ValueError("Conversion rule mutated model attribute.")
        return model.__class__(a=operands["a"])

    def map_Z(self, model, operands):
        if model.a == operands["a"]:
            raise ValueError("Conversion rule mutated model attribute.")
        return model.__class__(a=operands["a"])

    def map_dict(self, model, operands):
        if model == operands:
            raise ValueError("Conversion rule mutated model attribute.")
        return {k: v for k, v in operands.items() if k == "aa"}

    def map_list(self, model, operands):
        if model == operands:
            raise ValueError("Conversion rule mutated model attribute.")
        return reversed(operands)

    def map_tuple(self, model, operands):
        if model == operands:
            raise ValueError("Conversion rule mutated model attribute.")
        return reversed(operands)

    def map_int(self, model, operands):
        return model + 1


########################################################################################


class TestConversionRule:
    @pytest.fixture
    def custom_pass(self):
        return Post(CustomRule())

    @pytest.mark.parametrize(
        "model",
        [
            X(a=dict(aa=1, ab=2)),
            Y(a=[1, 2, 3, 4, 5]),
            Z(a=(1, 2)),
        ],
    )
    def test_conversion_model_argument_attribute_unmodified(self, model, custom_pass):
        assert custom_pass(model) == model

    @pytest.fixture
    def custom_pass2(self):
        return Post(CustomRule2())

    @pytest.mark.parametrize(
        ("model", "out"),
        [
            (X(a=dict(aa=1, ab=2)), X(a=dict(aa=2))),
            (Y(a=[1, 2, 3, 4, 5]), Y(a=[6, 5, 4, 3, 2])),
            (Z(a=(1, 2)), Z(a=(3, 2))),
        ],
    )
    def test_conversion_with_dict_tuple_int_rule(self, model, out, custom_pass2):
        assert custom_pass2(model) == out
