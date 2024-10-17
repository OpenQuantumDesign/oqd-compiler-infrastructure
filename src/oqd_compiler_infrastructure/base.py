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

from abc import ABC, abstractmethod

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
        pass

    @property
    @abstractmethod
    def children(self):
        pass

    def __call__(self, model):
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
