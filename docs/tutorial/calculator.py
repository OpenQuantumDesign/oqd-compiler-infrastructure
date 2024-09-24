from typing import List

from pydantic import conlist, computed_field

########################################################################################

import oqd_compiler_infrastructure as ci

########################################################################################


class MyMath(ci.TypeReflectBaseModel):

    def __add__(self, other):
        return MyAdd(expressions=[self, other])

    pass


class MyInteger(MyMath):

    value: int


class MyAdd(MyMath):
    class_: Literal["MyAdd"]
    expressions: List[MyMath]


class MyMul(MyMath):
    class_: Literal["MyMul"]
    expressions: List[MyMath]


class MyPow(MyMath):
    expression: MyMath
    exponent: MyMath


class Chain(ci.VisitableBaseModel):
    ions: List[Ion]
    trap_freqs: conlist(float, 3, 3)
    selected_modes: List[int]
    pass


class Laser(ci.VisitableBaseModel): ...


class Chamber(ci.VisitableBaseModel):
    chain: Chain
    magnetic_field: conlist(float, 3, 3) = [0, 0, 1]
    lasers: Laser

    @computed_field
    def L(self):
        return self.chain


class Chamber2operator(ci.ConversionRule):
    def map_Chamber(self, model, operands) -> Operator:
        return sum(operands["lasers"]) + operands["chain"]

    def map_Chain(self, model, operands) -> Operator:
        self.ions = model.ions

        operator = construct_atoomic_hamiltonian(model)
        
        return operator

    def map_Laser(self,model,operands) -> Operator:
        operator = ZeroOperator()
        for ion in self.ions:
            for transition in ion.transitions:
                    ...
                
                operator += construct_laser_hamiltonian(...)
            
        return operator