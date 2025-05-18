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
    Chain,
    ConversionRule,
    FixedPoint,
    Post,
    RewriteRule,
    TypeReflectBaseModel,
)

########################################################################################


class MyMath(TypeReflectBaseModel):
    def __add__(self, other):
        if isinstance(other, MyMath):
            return MyAdd(left=self, right=other)
        else:
            raise TypeError("Invalid type for other")


class MyInt(MyMath):
    x: int


class MyAdd(MyMath):
    left: MyInt
    right: MyInt


########################################################################################


class MyEvaluate(ConversionRule):
    def map_MyInt(self, model, operands):
        return model.x

    def map_MyAdd(self, model, operands):
        return operands["left"] + operands["right"]


class MySimplify(RewriteRule):
    def map_MyAdd(self, model):
        if isinstance(model.left, MyInt) and isinstance(model.right, MyInt):
            return MyInt(x=model.left.x + model.right.x)


########################################################################################
@pytest.fixture
def model():
    return MyInt(x=1) + MyInt(x=2)


########################################################################################


class TestChain:
    def test_chain_interpreter(self, model):
        interpreter_pass = Chain(
            Post(MySimplify()),
            Post(MyEvaluate()),
        )

        new_model = interpreter_pass(model)

        assert new_model == 3


########################################################################################


class TestFixedPoint:
    def test_fixed_point_simplify(self, model):
        rewrite_pass = FixedPoint(Post(MySimplify()))

        new_model = rewrite_pass(model)

        assert new_model == MyInt(x=3)
