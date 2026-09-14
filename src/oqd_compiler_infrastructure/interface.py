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

from abc import abstractmethod
from collections.abc import MutableMapping
from typing import Iterable, Literal, TypeVar

from pydantic import BaseModel, ConfigDict

########################################################################################

__all___ = [
    "VisitableBaseModel",
    "TypeReflectBaseModel",
]

########################################################################################


class VisitableBaseModel(BaseModel):
    """
    Class representing a visitable datastruct
    """

    model_config = ConfigDict(validate_assignment=True)

    def accept(self, pass_):
        return pass_(self)


class TypeReflectBaseModel(VisitableBaseModel):
    """
    Class representing a datastruct with type reflection
    """

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.__annotations__ = dict(class_=Literal[cls.__name__], **cls.__annotations__)
        setattr(cls, "class_", cls.__name__)


########################################################################################

LabelType = TypeVar("LabelType")
NodeType = TypeVar("NodeType")


class GraphProtocol(MutableMapping[LabelType, NodeType]):
    """
    Any object passed to `DataflowAnalysis.analyze` must provide this interface.
    The protocol is intentionally minimal so it can adapt to Control Flow Graphs (CFGs),
    dependency graphs, custom IR graphs, etc.
    """

    @abstractmethod
    def nodes(self) -> Iterable[LabelType]:
        """Returns all nodes in the graph."""
        ...

    @abstractmethod
    def predecessors(self, node: LabelType) -> Iterable[LabelType]:
        """Returns all predecessors of a given node."""
        ...

    @abstractmethod
    def successors(self, node: LabelType) -> Iterable[LabelType]:
        """Returns all successors of a given node."""
        ...
