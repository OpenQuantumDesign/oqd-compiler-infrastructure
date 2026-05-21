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

NodeType = TypeVar("NodeType")
StateType = TypeVar("StateType")

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
class DataflowResult(Generic[NodeType, StateType]):
    """
    The result of a dataflow analysis.
    """
    in_states: dict[NodeType, StateType]
    out_states: dict[NodeType, StateType]
    iterations: int


class DataflowAnalysis(ABC, Generic[NodeType, StateType]):
    """
    Base class that defines what every dataflow analysis must implement.
    """
    @abstractmethod
    def bottom(self) -> StateType:
        """Returns the default starting state for all nodes."""
        pass

    @abstractmethod
    def boundary_state(self, node: NodeType) -> StateType:
        """Returns the extra state injected at a given node."""
        pass

    @abstractmethod
    def merge(self, states: Iterable[StateType]) -> StateType:
        """Returns the combined state of incoming states."""
        pass

    @abstractmethod
    def transfer(self, node: NodeType, state_in: StateType) -> StateType:
        """Returns the state of a given node after transfer."""
        pass

    def states_equal(self, t1: StateType, t2: StateType) -> bool:
        """Returns True if two states are equal."""
        return t1 == t2


class ForwardDataflowAnalysis(DataflowAnalysis[NodeType, StateType], Generic[NodeType, StateType]):
    """
    Forward dataflow analysis framework.
    This class implements the fixed point loop.
    """
    def analyze(self, graph: GraphProtocol[NodeType]) -> DataflowResult[NodeType, StateType]:
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
            merged_input = self.merge([self.boundary_state(node), *pred_states])

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

