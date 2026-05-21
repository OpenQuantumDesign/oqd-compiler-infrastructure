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
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

########################################################################################


class TTop:
    pass


class TBottom(TTop):
    pass


LatticeType = TypeVar("LatticeType")


class Lattice(ABC, Generic[LatticeType]):
    @abstractmethod
    def leq(self, t1: LatticeType, t2: LatticeType) -> bool:
        pass
    @abstractmethod
    def join(self, t1: LatticeType, t2: LatticeType) -> LatticeType:
        pass
    @abstractmethod
    def meet(self, t1: LatticeType, t2: LatticeType) -> LatticeType:
        pass


class LatticeBase(Lattice[LatticeType]):

    def __init__(self):
        self.parents = {
            TBottom: (),
            TTop: (),
        }
    
    def is_class_token(self, t: object) -> bool:
        return isinstance(t, type) and issubclass(t, TTop)
    
    def add_parent(self, t, parent):
        self.parents[t] = (parent,)
    
    def atomic_ancestors(self, t):
        if not self.is_class_token(t):
            raise TypeError(f"Expected lattice class token, got {t}")
        out = {t}
        stack = [t]
        while stack:
            curr = stack.pop()
            for parent in self.parents.get(curr, ()):
                if parent not in out:
                    out.add(parent)
                    stack.append(parent)
        return out
    
    def leq(self, t1: LatticeType, t2: LatticeType) -> bool:
        if t1 is TBottom:
            return True
        if not self.is_class_token(t1) or not self.is_class_token(t2):
            return False
        if t1 is t2:
            return True
        return t2 in self.atomic_ancestors(t1)
    
    
    def join(self, t1: LatticeType, t2: LatticeType) -> LatticeType:
        if self.leq(t1, t2):
            return t2
        if self.leq(t2, t1):
            return t1
        if not self.is_class_token(t1) or not self.is_class_token(t2):
            return TTop
        common_ancestors = self.atomic_ancestors(t1).intersection(self.atomic_ancestors(t2))
        if not common_ancestors:
            return TTop
        
        minimal_ancestors = set()
        for candidate in common_ancestors:
            smaller = any(
                other is not candidate and self.leq(other, candidate)
                for other in common_ancestors
            )
            if not smaller:
                minimal_ancestors.add(candidate)
        if len(minimal_ancestors) != 1:
            return TTop
        return next(iter(minimal_ancestors))
    
    
    def meet(self, t1: LatticeType, t2: LatticeType) -> LatticeType:
        if self.leq(t1, t2):
            return t1
        if self.leq(t2, t1):
            return t2
        return TBottom
    
