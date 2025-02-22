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
    AnalysisCache,
    AnalysisRequirements,
    AnalysisResult,
    AnalysisRule,
    Chain,
    ConversionRule,
    FixedPoint,
    Post,
    Pre,
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
class CountTerms(AnalysisRule):
    def __init__(self):
        super().__init__()

        self.N_terms = 0

    @property
    def analysis_data(self):
        return dict(N_terms=self.N_terms)

    def map_MyInt(self, model):
        self.N_terms += 1


class CountAdds(AnalysisRule):
    def __init__(self):
        super().__init__()

        self.N_terms = 0

    @property
    def analysis_data(self):
        return dict(N_terms=self.N_terms)

    def map_MyAdd(self, model):
        self.N_terms += 1


class WalkOrder(AnalysisRule):
    def __init__(self):
        super().__init__()

        self.walk_order = []
        self.counter = 0

    @property
    def analysis_data(self):
        return dict(walk_order=self.walk_order, counter=self.counter)

    def generic_map(self, model):
        self.walk_order.append((self.counter, model))
        self.counter += 1


########################################################################################


class RequiresSingle(RewriteRule):
    analysis_requirements = AnalysisRequirements(requirements=[CountTerms])


class RequiresMultiple(RewriteRule):
    analysis_requirements = AnalysisRequirements(requirements=[CountTerms, CountAdds])


class RequiresPostWalk(RewriteRule):
    analysis_requirements = AnalysisRequirements(requirements=[WalkOrder])


class RequiresPreWalk(RewriteRule):
    analysis_requirements = AnalysisRequirements(requirements=[(WalkOrder, Pre)])


class MyEvaluate(ConversionRule):
    analysis_requirements = AnalysisRequirements(requirements=[CountTerms])

    def after_call(self, model):
        super().after_call(model)
        self.analysis_cache.invalidate("CountTerms")

    def map_MyInt(self, model, operands):
        return model.x

    def map_MyAdd(self, model, operands):
        return operands["left"] + operands["right"]


class MySimplify(RewriteRule):
    analysis_requirements = AnalysisRequirements(requirements=[CountTerms])

    def after_call(self, model):
        super().after_call(model)
        self.analysis_cache.invalidate("CountTerms")

    def map_MyAdd(self, model):
        if isinstance(model.left, MyInt) and isinstance(model.right, MyInt):
            return MyInt(x=model.left.x + model.right.x)


########################################################################################


def verify_shared_analysis_cache(analysis_pass):
    for child in analysis_pass.children:
        assert analysis_pass.analysis_cache == child.analysis_cache
        verify_shared_analysis_cache(child)


#######################################################################################


@pytest.fixture
def model():
    return MyInt(x=1) + MyInt(x=2)


def test_walk_shared_analysis_cache(model):
    analysis_pass = Post(CountTerms())

    analysis_pass(model)

    verify_shared_analysis_cache(analysis_pass)


def test_chain_shared_analysis_cache(model):
    analysis_pass = Chain(Post(CountTerms()), Post(CountTerms()))

    analysis_pass(model)

    verify_shared_analysis_cache(analysis_pass)


def test_fixed_point_shared_analysis_cache(model):
    analysis_pass = FixedPoint(Post(CountTerms()))

    analysis_pass(model)

    verify_shared_analysis_cache(analysis_pass)


########################################################################################


def test_simple_analysis_pass(model):
    analysis_pass = Post(CountTerms())

    analysis_pass(model)

    assert analysis_pass.analysis_cache == AnalysisCache(
        store=[AnalysisResult(name="CountTerms", valid=True, data=dict(N_terms=2))]
    )


def test_repeat_analysis_pass(model):
    analysis_pass = Chain(Post(CountTerms()), Post(CountTerms()))

    analysis_pass(model)

    assert analysis_pass.analysis_cache == AnalysisCache(
        store=[
            AnalysisResult(name="CountTerms", valid=False, data=dict(N_terms=2)),
            AnalysisResult(name="CountTerms", valid=True, data=dict(N_terms=2)),
        ]
    )


def test_fixed_point_analysis_pass(model):
    analysis_pass = FixedPoint(Post(CountTerms()))

    analysis_pass(model)

    assert analysis_pass.analysis_cache == AnalysisCache(
        store=[
            AnalysisResult(name="CountTerms", valid=True, data=dict(N_terms=2)),
        ]
    )


def test_chain_analysis_pass(model):
    analysis_pass = Chain(Post(CountTerms()), Post(CountAdds()))

    analysis_pass(model)

    assert analysis_pass.analysis_cache == AnalysisCache(
        store=[
            AnalysisResult(name="CountTerms", valid=True, data=dict(N_terms=2)),
            AnalysisResult(name="CountAdds", valid=True, data=dict(N_terms=1)),
        ]
    )


########################################################################################


def test_single_automated_analysis(model):
    analysis_pass = Post(RequiresSingle())

    analysis_pass(model)

    assert analysis_pass.analysis_cache == AnalysisCache(
        store=[
            AnalysisResult(name="CountTerms", valid=True, data=dict(N_terms=2)),
        ]
    )


def test_multiple_automated_analysis(model):
    analysis_pass = Post(RequiresMultiple())

    analysis_pass(model)

    assert analysis_pass.analysis_cache == AnalysisCache(
        store=[
            AnalysisResult(name="CountTerms", valid=True, data=dict(N_terms=2)),
            AnalysisResult(name="CountAdds", valid=True, data=dict(N_terms=1)),
        ]
    )


def test_requires_post_walk_automated_analysis(model):
    analysis_pass = Post(RequiresPostWalk())

    analysis_pass(model)

    assert analysis_pass.analysis_cache == AnalysisCache(
        store=[
            AnalysisResult(
                name="WalkOrder",
                valid=True,
                data=dict(
                    walk_order=[
                        (0, 1),
                        (1, MyInt(class_="MyInt", x=1)),
                        (2, 2),
                        (3, MyInt(class_="MyInt", x=2)),
                        (
                            4,
                            MyAdd(
                                class_="MyAdd",
                                left=MyInt(class_="MyInt", x=1),
                                right=MyInt(class_="MyInt", x=2),
                            ),
                        ),
                    ],
                    counter=5,
                ),
            ),
        ]
    )


def test_requires_pre_walk_automated_analysis(model):
    analysis_pass = Post(RequiresPreWalk())

    analysis_pass(model)

    assert analysis_pass.analysis_cache == AnalysisCache(
        store=[
            AnalysisResult(
                name="WalkOrder",
                valid=True,
                data=dict(
                    walk_order=[
                        (
                            0,
                            MyAdd(
                                class_="MyAdd",
                                left=MyInt(class_="MyInt", x=1),
                                right=MyInt(class_="MyInt", x=2),
                            ),
                        ),
                        (1, MyInt(class_="MyInt", x=1)),
                        (2, 1),
                        (3, MyInt(class_="MyInt", x=2)),
                        (4, 2),
                    ],
                    counter=5,
                ),
            ),
        ]
    )


########################################################################################


def test_simplify_automated_analysis(model):
    simplify_pass = Post(MySimplify())

    new_model = simplify_pass(model)

    assert new_model == MyInt(x=3)
    assert simplify_pass.analysis_cache == AnalysisCache(
        store=[
            AnalysisResult(name="CountTerms", valid=False, data=dict(N_terms=2)),
        ]
    )


def test_chain_simplify_automated_analysis(model):
    simplify_pass = Chain(Post(MySimplify()), Post(MySimplify()))

    new_model = simplify_pass(model)

    assert new_model == MyInt(x=3)
    assert simplify_pass.analysis_cache == AnalysisCache(
        store=[
            AnalysisResult(name="CountTerms", valid=False, data=dict(N_terms=2)),
            AnalysisResult(name="CountTerms", valid=False, data=dict(N_terms=1)),
        ]
    )


def test_evaluate_automated_analysis(model):
    evaluate_pass = Post(MyEvaluate())

    new_model = evaluate_pass(model)

    assert new_model == 3
    assert evaluate_pass.analysis_cache == AnalysisCache(
        store=[
            AnalysisResult(name="CountTerms", valid=False, data=dict(N_terms=2)),
        ]
    )


def test_chain_evaluate_automated_analysis(model):
    evaluate_pass = Chain(Post(MyEvaluate()), Post(MyEvaluate()))

    new_model = evaluate_pass(model)

    assert new_model == 3
    assert evaluate_pass.analysis_cache == AnalysisCache(
        store=[
            AnalysisResult(name="CountTerms", valid=False, data=dict(N_terms=2)),
            AnalysisResult(name="CountTerms", valid=False, data=dict(N_terms=0)),
        ]
    )
