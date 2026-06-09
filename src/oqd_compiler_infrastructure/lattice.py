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
import types
from abc import ABC, abstractmethod
from typing import Dict, Generic, Type, TypeVar

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


LatticeValue = TypeVar("LatticeValue")


class Lattice(ABC, Generic[LatticeValue], metaclass=Singleton):
    """
    Abstract base class for a lattice interface.
    """

    @abstractmethod
    def top(self) -> LatticeValue:
        """Returns the top element of the lattice."""
        pass

    @abstractmethod
    def bottom(self) -> LatticeValue:
        """Returns the bottom element of the lattice."""
        pass

    @abstractmethod
    def leq(self, t1: LatticeValue, t2: LatticeValue) -> bool:
        """Returns True if `t1 <= t2` in the lattice."""
        pass

    @abstractmethod
    def join(self, t1: LatticeValue, t2: LatticeValue) -> LatticeValue:
        """Returns the least upper bound of `t1` and `t2`."""
        pass

    @abstractmethod
    def meet(self, t1: LatticeValue, t2: LatticeValue) -> LatticeValue:
        """Returns the greatest lower bound of `t1` and `t2`."""
        pass
    
    def equal(self, t1: LatticeValue, t2: LatticeValue) -> bool:
        """Returns True if two values are equal in the lattice."""
        return self.leq(t1, t2) and self.leq(t2, t1)


class LatticeBase(Lattice[LatticeValue]):
    """
    Concrete implementation of a lattice interface.
    """
    
    def top(self) -> LatticeValue:
        """Returns the top element of the lattice."""
        return LatticeTop

    def bottom(self) -> LatticeValue:
        """Returns the bottom element of the lattice."""
        return LatticeBottom

    def is_class_node(self, t: object) -> bool:
        """Returns True if `t` is a valid lattice node."""
        return isinstance(t, type) and issubclass(t, LatticeTop)

    def atomic_ancestors(self, t: object) -> set[object]:
        """Returns the atomic ancestors of a given node."""
        if not self.is_class_node(t):
            raise TypeError(f"Expected lattice class node, got {t}")
        return {c for c in t.__mro__ if self.is_class_node(c)}

    def leq(self, t1: LatticeValue, t2: LatticeValue) -> bool:
        """Returns True if `t1 <= t2` in the lattice."""
        if t1 is LatticeBottom:
            return True
        if not self.is_class_node(t1) or not self.is_class_node(t2):
            return False
        if t1 is t2:
            return True
        return t2 in self.atomic_ancestors(t1)

    def join(self, t1: LatticeValue, t2: LatticeValue) -> LatticeValue:
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

    def meet(self, t1: LatticeValue, t2: LatticeValue) -> LatticeValue:
        """Returns the greatest lower bound of `t1` and `t2`."""
        if self.leq(t1, t2):
            return t1
        if self.leq(t2, t1):
            return t2
        return LatticeBottom


def maplattice(lattice: Type[Lattice]) -> Type[Lattice]:
    """Builds a map lattice class from a lattice class for map based analysis"""
    name = f"Map{lattice.__name__}"

    def wraps(f):
        f.__qualname__ = f"{name}.{f.__name__}"
        return f

    @wraps
    def top(self) -> LatticeValue:
        """Returns the top element of the lattice."""
        return LatticeTop

    @wraps
    def bottom(self) -> LatticeValue:
        """Returns the bottom element of the lattice."""
        return LatticeBottom

    @wraps
    def leq(self, t1: LatticeValue, t2: LatticeValue) -> bool:
        """Returns True if `t1 <= t2` in the lattice."""

        if t1 is LatticeBottom or t2 is LatticeTop:
            return True
        if t1 is LatticeTop:
            return t2 is LatticeTop
        if t2 is LatticeBottom:
            return self.leq(t1, {})
        v = self._element_lattice()
        b = v.bottom()
        for k in set(t1).union(t2):
            if not v.leq(t1.get(k, b), t2.get(k, b)):
                return False
        return True

    @wraps
    def join(self, t1: LatticeValue, t2: LatticeValue) -> LatticeValue:
        """Returns the least upper bound of `t1` and `t2`."""

        if t1 is LatticeTop or t2 is LatticeTop:
            return LatticeTop
        if t1 is LatticeBottom:
            return t2
        if t2 is LatticeBottom:
            return t1
        v = self._element_lattice()
        b = v.bottom()
        return {k: v.join(t1.get(k, b), t2.get(k, b)) for k in set(t1).union(t2)}

    @wraps
    def meet(self, t1: LatticeValue, t2: LatticeValue) -> LatticeValue:
        """Returns the greatest lower bound of `t1` and `t2`."""

        if t1 is LatticeBottom or t2 is LatticeBottom:
            return LatticeBottom
        if t1 is LatticeTop:
            return t2
        if t2 is LatticeTop:
            return t1
        v = self._element_lattice()
        b = v.bottom()
        return {k: v.meet(t1.get(k, b), t2.get(k, b)) for k in set(t1).union(t2)}

    def update_ns(ns):
        ns.update(
            {
                "__module__": lattice.__module__,
                "top": top,
                "bottom": bottom,
                "leq": leq,
                "join": join,
                "meet": meet,
                "_element_lattice": lattice,
            }
        )
        return ns

    cls = types.new_class(name, (Lattice[Dict[str, LatticeValue]],), None, update_ns)
    return cls


PowersetValue = set | type[LatticeTop]

class PowersetLattice(Lattice[PowersetValue]):
    def top(self) -> PowersetValue:
        return LatticeTop
    
    def bottom(self) -> PowersetValue:
        return set()
    
    def leq(self, t1: PowersetValue, t2: PowersetValue) -> bool:
        if t2 is LatticeTop:
            return True
        if t1 is LatticeTop:
            return False
        return t1 <= t2
    
    def join(self, t1: PowersetValue, t2: PowersetValue) -> PowersetValue:
        if t1 is LatticeTop or t2 is LatticeTop:
            return LatticeTop
        return t1 | t2
    
    def meet(self, t1: PowersetValue, t2: PowersetValue) -> PowersetValue:
        if t1 is LatticeTop:
            return t2
        if t2 is LatticeTop:
            return t1
        return t1 & t2

