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
from collections import deque
from dataclasses import dataclass
from typing import Generic, Iterable, TypeVar, Protocol
from oqd_compiler_infrastructure.lattice import Lattice, LatticeType

NodeType = TypeVar("NodeType")

class GraphProtocol(Protocol[NodeType]):
    """
    Any object passed to `ForwardDataflowAnalysis.analyze` must provide this interface. 
    The protocol is intentionally minimal so it can adapt to Control Flow Graphs (CFGs),
    dependency graphs, custom IR graphs, etc.
    """
    def nodes(self) -> Iterable[NodeType]:
        """ Returns all nodes in the graph. """
        ...
    def predecessors(self, node: NodeType) -> Iterable[NodeType]:
        """ Returns all predecessors of a given node. """
        ...
    def successors(self, node: NodeType) -> Iterable[NodeType]:
        """ Returns all successors of a given node. """
        ...


@dataclass(frozen=True)
class DataflowResult(Generic[NodeType, LatticeType]):
    """
    The result of a dataflow analysis.
    """
    in_states: dict[NodeType, LatticeType]
    out_states: dict[NodeType, LatticeType]
    iterations: int


class DataflowAnalysis(ABC, Generic[NodeType, LatticeType]):
    """
    Base class that defines what every dataflow analysis must implement.
    """

    def __init__(self, lattice: Lattice[LatticeType]):
        self.lattice = lattice
    
    @abstractmethod
    def transfer(self, node: NodeType, state_in: LatticeType) -> LatticeType:
        """Returns the state of a given node after transfer."""
        pass
    
    def bottom(self) -> LatticeType:
        """Returns the default starting state for all nodes."""
        return self.lattice.bottom()

    def merge(self, states: Iterable[LatticeType]) -> LatticeType:
        """Joins incoming states using the lattice's join operation."""
        states_list = list(states)
        if not states_list:
            return self.bottom()
        merged = states_list[0]
        for state in states_list[1:]:
            merged = self.lattice.join(merged, state)
        return merged

    def states_equal(self, t1: LatticeType, t2: LatticeType) -> bool:
        """Returns True if two states are equal in the lattice."""
        return self.lattice.leq(t1, t2) and self.lattice.leq(t2, t1)


class ForwardDataflowAnalysis(DataflowAnalysis[NodeType, LatticeType], Generic[NodeType, LatticeType]):
    """
    Forward dataflow analysis framework.
    """
    def __init__(self, lattice: Lattice[LatticeType]):
        super().__init__(lattice)
    
    def analyze(self, graph: GraphProtocol[NodeType]) -> DataflowResult[NodeType, LatticeType]:
        """
        Runs the worklist algorithm and returns the result of the dataflow analysis.
        Steps:
        - Initializes in/out states with `bottom()`.
        - Puts all nodes in a worklist.
        - Recomputes each node from predecessor outputs.
        - If a node output changes, schedules its successors again.
        - Returns final states and iteration count.
        """
        nodes = list(graph.nodes())
        in_states = {node: self.bottom() for node in nodes}
        out_states = {node: self.bottom() for node in nodes}

        worklist = deque(nodes)
        queued = set(nodes)
        iterations = 0

        while worklist:
            node = worklist.popleft()
            queued.discard(node)
            iterations += 1

            pred_states = [out_states[pred] for pred in graph.predecessors(node)]
            merged_input = self.merge(pred_states)

            if not self.states_equal(in_states[node], merged_input):
                in_states[node] = merged_input

            next_out = self.transfer(node, merged_input)
            if self.states_equal(out_states[node], next_out):
                continue

            out_states[node] = next_out
            for succ in graph.successors(node):
                if succ not in queued:
                    worklist.append(succ)
                    queued.add(succ)
                    
        return DataflowResult(in_states=in_states, out_states=out_states, iterations=iterations)


class MapForwardDataflowAnalysis(ForwardDataflowAnalysis[NodeType, dict[str, LatticeType]], Generic[NodeType, LatticeType]):
    """
    Helper instance of ForwardDataflowAnalysis for states that need a dict Type.
    """
    def __init__(self, lattice: Lattice[LatticeType]):
        super().__init__(lattice)
    
    def bottom(self) -> dict[str, LatticeType]:
        return {}
    
    def merge(self, states: Iterable[dict[str, LatticeType]]) -> dict[str, LatticeType]:
        states_list = list(states)
        if not states_list:
            return {}
        
        bottom = self.bottom()
        all_keys = set().union(*(state.keys() for state in states_list))
            
        merged = {}
        for name in all_keys:
            value = bottom
            for state in states_list:
                value = self.lattice.join(value, state.get(name, bottom))
            merged[name] = value
        
        return merged
    
    def states_equal(self, t1: dict[str, LatticeType], t2: dict[str, LatticeType]) -> bool:
        bottom = self.bottom()
        all_keys = set(t1.keys()).union(t2.keys())
        
        for key in all_keys:
            v1 = t1.get(key, bottom)
            v2 = t2.get(key, bottom)
            if not (self.lattice.leq(v1, v2) and self.lattice.leq(v2, v1)):
                return False
        
        return True

