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

from .meta import Singleton

########################################################################################


class LatticeTop:
    """
    Base class representing the top element of the lattice.
    In `LatticeBase`, nodes are classes that inherit from `LatticeTop`.
    """

    pass


class LatticeBottom(LatticeTop):
    """
    Base class representing the bottom element of the lattice.
    """

    pass


LatticeType = TypeVar("LatticeType")


class Lattice(ABC, Generic[LatticeType], metaclass=Singleton):
    """
    Abstract base class for a lattice interface.
    """

    @abstractmethod
    def bottom(self) -> LatticeType:
        """Returns the bottom element of the lattice."""
        pass

    @abstractmethod
    def leq(self, t1: LatticeType, t2: LatticeType) -> bool:
        """Returns True if `t1 <= t2` in the lattice."""
        pass

    @abstractmethod
    def join(self, t1: LatticeType, t2: LatticeType) -> LatticeType:
        """Returns the least upper bound of `t1` and `t2`."""
        pass

    @abstractmethod
    def meet(self, t1: LatticeType, t2: LatticeType) -> LatticeType:
        """Returns the greatest lower bound of `t1` and `t2`."""
        pass


class LatticeBase(Lattice[LatticeType]):
    """
    Concrete implementation of a lattice interface.
    """

    def __init__(self):
        """
        Initializes lattice with top and bottom nodes.
        The map is a dictionary that maps each node of the lattice to its immediate parent(s).
        """
        self.map_node_to_parents = {
            LatticeBottom: (),
            LatticeTop: (),
        }

    def bottom(self) -> LatticeType:
        """Returns the bottom element of the lattice."""
        return LatticeBottom

    def is_class_node(self, t: object) -> bool:
        """Returns True if `t` is a valid lattice node."""
        return isinstance(t, type) and issubclass(t, LatticeTop)

    def add_node(self, t: object, parent: object) -> None:
        """Adds a node to the lattice, by tracking the parent(s) of the node."""
        self.map_node_to_parents[t] = (parent,)

    def atomic_ancestors(self, t: object) -> set[object]:
        """Returns the atomic ancestors of a given node."""
        if not self.is_class_node(t):
            raise TypeError(f"Expected lattice class node, got {t}")
        out = {t}
        stack = [t]
        while stack:
            curr = stack.pop()
            for parent in self.map_node_to_parents.get(curr, ()):
                if parent not in out:
                    out.add(parent)
                    stack.append(parent)
        return out

    def leq(self, t1: LatticeType, t2: LatticeType) -> bool:
        """Returns True if `t1 <= t2` in the lattice."""
        if t1 is LatticeBottom:
            return True
        if not self.is_class_node(t1) or not self.is_class_node(t2):
            return False
        if t1 is t2:
            return True
        return t2 in self.atomic_ancestors(t1)

    def join(self, t1: LatticeType, t2: LatticeType) -> LatticeType:
        """Returns the least upper bound of `t1` and `t2`."""
        if self.leq(t1, t2):
            return t2
        if self.leq(t2, t1):
            return t1
        if not self.is_class_node(t1) or not self.is_class_node(t2):
            return LatticeTop
        common_ancestors = self.atomic_ancestors(t1).intersection(
            self.atomic_ancestors(t2)
        )
        if not common_ancestors:
            return LatticeTop

        minimal_ancestors = set()
        for candidate in common_ancestors:
            smaller = any(
                other is not candidate and self.leq(other, candidate)
                for other in common_ancestors
            )
            if not smaller:
                minimal_ancestors.add(candidate)
        if len(minimal_ancestors) != 1:
            return LatticeTop
        return next(iter(minimal_ancestors))

    def meet(self, t1: LatticeType, t2: LatticeType) -> LatticeType:
        """Returns the greatest lower bound of `t1` and `t2`."""
        if self.leq(t1, t2):
            return t1
        if self.leq(t2, t1):
            return t2
        return LatticeBottom


class MapLattice(Lattice[dict[str, LatticeType]], Generic[LatticeType]):
    """
    Helper instance of Lattice that builds a lattice for map states.
    """
    
    def __init__(self, value_lattice: Lattice[LatticeType]):
        self.value_lattice = value_lattice
    
    def bottom(self) -> dict[str, LatticeType]:
        return {}
    
    def leq(self, t1: dict[str, LatticeType], t2: dict[str, LatticeType]) -> bool:
        bottom = self.value_lattice.bottom()
        keys = set(t1.keys()).union(t2.keys())
        for k in keys:
            left_val = t1.get(k, bottom)
            right_val = t2.get(k, bottom)
            if not self.value_lattice.leq(left_val, right_val):
                return False
        return True
    
    def join(self, t1: dict[str, LatticeType], t2: dict[str, LatticeType]) -> dict[str, LatticeType]:
        bottom = self.value_lattice.bottom()
        keys = set(t1.keys()).union(t2.keys())
        out: dict[str, LatticeType] = {}
        for k in keys:
            out[k] = self.value_lattice.join(t1.get(k, bottom), t2.get(k, bottom))
        return out
    
    def meet(self, t1: dict[str, LatticeType], t2: dict[str, LatticeType]) -> dict[str, LatticeType]:
        bottom = self.value_lattice.bottom()
        keys = set(t1.keys()).union(t2.keys())
        out: dict[str, LatticeType] = {}
        for k in keys:
            out[k] = self.value_lattice.meet(t1.get(k, bottom), t2.get(k, bottom))
        return out
    
    
