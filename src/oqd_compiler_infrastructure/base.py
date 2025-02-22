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

from abc import ABC, abstractmethod

########################################################################################
from oqd_compiler_infrastructure.analysis import AnalysisCache

########################################################################################

__all__ = [
    "PassBase",
]

########################################################################################


class PassBase(ABC):
    """
    Abstract base class for passes.
    """

    def __init__(self):
        self._analysis_cache = None
        pass

    @property
    def analysis_cache(self):
        return self._analysis_cache

    @analysis_cache.setter
    def analysis_cache(self, value: AnalysisCache):
        if isinstance(value, AnalysisCache):
            self._analysis_cache = value
            return

        raise TypeError(f"Invalid type {type(value)} for analysis cache")

    @property
    @abstractmethod
    def children(self):
        pass

    def __call__(self, model):
        if self.analysis_cache is None:
            self.analysis_cache = AnalysisCache()

        for rule in self.children:
            rule.analysis_cache = self.analysis_cache

        self._model = model

        model = self.map(model)
        if model is None:
            model = self._model
        return model

    @abstractmethod
    def map(self, model):
        pass

    def __repr__(self):
        return "{}({})".format(
            self.__class__.__name__,
            ", ".join(
                f"{k}={v}" for k, v in self.__dict__.items() if not k.startswith("_")
            ),
        )
