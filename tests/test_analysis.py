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

########################################################################################
from oqd_compiler_infrastructure import (
    AnalysisCache,
    AnalysisResult,
    AnalysisRule,
    Chain,
    FixedPoint,
    Post,
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
