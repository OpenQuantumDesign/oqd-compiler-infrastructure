from typing import Optional, Literal
from pydantic import BaseModel, model_validator

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

    def accept(self, pass_):
        return pass_(self)

    class Config:
        validate_assignment = True


class TypeReflectBaseModel(VisitableBaseModel):
    """
    Class representing a datastruct with type reflection
    """

    class_: Optional[str]

    @model_validator(mode="before")
    @classmethod
    def reflect(cls, data):
        if isinstance(data, BaseModel):
            return data
        if "class_" in data.keys():
            if data["class_"] != cls.__name__:
                raise ValueError('discrepency between "class_" field and model type')

        data["class_"] = cls.__name__

        return data


    # @classmethod
    # def get_subclasses(cls):
    #     # necessary for deserializing subclassed operators
    #     def all_subclasses(cls):
    #         return set(cls.__subclasses__()).union(
    #             [s for c in cls.__subclasses__() for s in all_subclasses(c)])
    #     return tuple(all_subclasses(cls))
    #     # return tuple(cls.__subclasses__())
