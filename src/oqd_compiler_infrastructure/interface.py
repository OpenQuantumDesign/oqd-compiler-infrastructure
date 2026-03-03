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

from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, model_validator

########################################################################################

__all___ = [
    "NodeBaseModel",
    "VisitableBaseModel",
    "TypeReflectBaseModel",
]

########################################################################################


class NodeBaseModel(BaseModel):
    """
    Class representing a node datastruct
    """

    model_config = ConfigDict(validate_assignment=True)
    _parent: Optional[NodeBaseModel] = None

    def accept(self, pass_):
        return pass_(self)

    @model_validator(mode="after")
    def assign_parents(self):
        for k in self.__class__.model_fields.keys():
            if isinstance(getattr(self, k), VisitableBaseModel):
                getattr(self, k)._parent = self

            if isinstance(getattr(self, k), (list, tuple)):
                for x in getattr(self, k):
                    if isinstance(x, VisitableBaseModel):
                        x._parent = self

            if isinstance(getattr(self, k), dict):
                print(getattr(self, k).items())
                for dk, dv in getattr(self, k).items():
                    if isinstance(dv, VisitableBaseModel):
                        getattr(self, k)[dk]._parent = self

        return self


class VisitableBaseModel(NodeBaseModel):
    """
    Class representing a visitable datastruct
    """

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
