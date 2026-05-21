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
    """
    Base class representing the top element of the lattice.
    In `LatticeBase`, nodes are classes that inherit from `TTop`.
    """
    pass


class TBottom(TTop):
    """
    Base class representing the bottom element of the lattice.
    """
    pass


LatticeType = TypeVar("LatticeType")


class Lattice(ABC, Generic[LatticeType]):
    """
    Abstract base class for a lattice interface.
    """
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
            TBottom: (),
            TTop: (),
        }
    
    
    def is_class_node(self, t: object) -> bool:
        """Returns True if `t` is a valid lattice node."""
        return isinstance(t, type) and issubclass(t, TTop)
    
    
    def add_node(self, t, parent):
        """Adds a node to the lattice, by tracking the parent(s) of the node."""
        self.map_node_to_parents[t] = (parent,)
    
    
    def atomic_ancestors(self, t):
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
        if t1 is TBottom:
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
        """Returns the greatest lower bound of `t1` and `t2`."""
        if self.leq(t1, t2):
            return t1
        if self.leq(t2, t1):
            return t2
        return TBottom
    
