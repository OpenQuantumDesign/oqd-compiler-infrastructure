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


from __future__ import annotations

from typing import Annotated, Any, Dict, List, Tuple, Type

from pydantic import BeforeValidator, ConfigDict

########################################################################################
from oqd_compiler_infrastructure.interface import TypeReflectBaseModel

########################################################################################


def _analysis_name(value):
    if isinstance(value, str):
        return value
    else:
        return value.__class__.__name__


class AnalysisCache(TypeReflectBaseModel):
    store: List[AnalysisResult] = []

    def __getitem__(self, idx):
        return [entry for entry in self.store if entry.name == idx]

    def invalidate(self, name):
        name = _analysis_name(name)

        relevant_entries = filter(lambda entry: entry.valid, self[name])
        for entry in relevant_entries:
            entry.valid = False

    def append(self, entry: AnalysisResult):
        self.store.append(entry)


class AnalysisResult(TypeReflectBaseModel):
    name: Annotated[str, BeforeValidator(_analysis_name)]
    valid: bool = True
    data: Dict[str, Any]


########################################################################################


def validate_analysis_requirement(value):
    if isinstance(value, tuple):
        return value
    else:
        return (value, Post)


class AnalysisRequirements(TypeReflectBaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    requirements: List[
        Annotated[
            Tuple[Type[AnalysisRule], Type[WalkBase]],
            BeforeValidator(validate_analysis_requirement),
        ]
    ] = []


########################################################################################

from oqd_compiler_infrastructure.rule import AnalysisRule  # noqa: E402
from oqd_compiler_infrastructure.walk import Post, WalkBase  # noqa: E402

AnalysisRequirements.model_rebuild()
