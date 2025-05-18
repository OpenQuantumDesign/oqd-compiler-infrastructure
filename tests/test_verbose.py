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


import io
from contextlib import redirect_stdout

import pytest

from oqd_compiler_infrastructure import (
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


class MySimplify(RewriteRule):
    def map_MyAdd(self, model):
        if isinstance(model.left, MyInt) and isinstance(model.right, MyInt):
            return MyInt(x=model.left.x + model.right.x)


########################################################################################
@pytest.fixture
def model():
    return MyInt(x=1) + MyInt(x=2)


########################################################################################


def capture(rewrite_pass, model):
    f = io.StringIO()
    with redirect_stdout(f):
        new_model = rewrite_pass(model)
    out = f.getvalue()
    return new_model, out.strip()


class TestVerbose:
    def test_single_verbose(self, model):
        simplify_pass = Post(MySimplify())

        simplify_pass.set_verbose(True)

        new_model, out = capture(simplify_pass, model)

        assert (
            out
            == """
Running Post(rule=MySimplify(), reverse=False) on MyAdd(class_='MyAdd' left=MyInt(class_='MyInt', x=1) right=MyInt(class_='MyInt', x=2))
Completed Post(rule=MySimplify(), reverse=False) on MyAdd(class_='MyAdd' left=MyInt(class_='MyInt', x=1) right=MyInt(class_='MyInt', x=2))
""".strip()
        )
        assert new_model == MyInt(x=3)

    def test_cascade_verbose(self, model):
        simplify_pass = Post(MySimplify())

        simplify_pass.set_verbose(True, cascade=True)

        new_model, out = capture(simplify_pass, model)

        assert (
            out
            == """
Running Post(rule=MySimplify(), reverse=False) on MyAdd(class_='MyAdd' left=MyInt(class_='MyInt', x=1) right=MyInt(class_='MyInt', x=2))
Running MySimplify() on int(1)
Completed MySimplify() on int(1)
Running MySimplify() on MyInt(class_='MyInt' x=1)
Completed MySimplify() on MyInt(class_='MyInt' x=1)
Running MySimplify() on int(2)
Completed MySimplify() on int(2)
Running MySimplify() on MyInt(class_='MyInt' x=2)
Completed MySimplify() on MyInt(class_='MyInt' x=2)
Running MySimplify() on MyAdd(class_='MyAdd' left=MyInt(class_='MyInt', x=1) right=MyInt(class_='MyInt', x=2))
Completed MySimplify() on MyAdd(class_='MyAdd' left=MyInt(class_='MyInt', x=1) right=MyInt(class_='MyInt', x=2))
Completed Post(rule=MySimplify(), reverse=False) on MyAdd(class_='MyAdd' left=MyInt(class_='MyInt', x=1) right=MyInt(class_='MyInt', x=2))
""".strip()
        )
        assert new_model == MyInt(x=3)

    def test_single_exclude_verbose(self, model):
        simplify_pass = Post(MySimplify())

        simplify_pass.set_verbose(True, exclude=(Post))

        new_model, out = capture(simplify_pass, model)

        assert out == ""
        assert new_model == MyInt(x=3)

    def test_cascade_exclude_verbose(self, model):
        simplify_pass = Post(MySimplify())

        simplify_pass.set_verbose(True, cascade=True, exclude=(MySimplify))

        new_model, out = capture(simplify_pass, model)

        assert (
            out
            == """
Running Post(rule=MySimplify(), reverse=False) on MyAdd(class_='MyAdd' left=MyInt(class_='MyInt', x=1) right=MyInt(class_='MyInt', x=2))
Completed Post(rule=MySimplify(), reverse=False) on MyAdd(class_='MyAdd' left=MyInt(class_='MyInt', x=1) right=MyInt(class_='MyInt', x=2))
""".strip()
        )
        assert new_model == MyInt(x=3)
