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
from typing import ClassVar, Generic, Iterable, TypeVar, Protocol, Callable
from oqd_compiler_infrastructure.lattice import Lattice, LatticeValue

NodeType = TypeVar("NodeType")


class GraphProtocol(Protocol[NodeType]):
    """
    Any object passed to `DataflowAnalysis.analyze` must provide this interface.
    The protocol is intentionally minimal so it can adapt to Control Flow Graphs (CFGs),
    dependency graphs, custom IR graphs, etc.
    """

    def nodes(self) -> Iterable[NodeType]:
        """Returns all nodes in the graph."""
        ...

    def predecessors(self, node: NodeType) -> Iterable[NodeType]:
        """Returns all predecessors of a given node."""
        ...

    def successors(self, node: NodeType) -> Iterable[NodeType]:
        """Returns all successors of a given node."""
        ...


@dataclass(frozen=True)
class DataflowResult(Generic[NodeType, LatticeValue]):
    """
    The result of a dataflow analysis.
    """

    in_states: dict[NodeType, LatticeValue]
    out_states: dict[NodeType, LatticeValue]
    iterations: int


class DataflowAnalysis(ABC, Generic[NodeType, LatticeValue]):
    """
    Base class that defines what every dataflow analysis must implement.
    """

    lattice: ClassVar[Lattice[LatticeValue]]

    @abstractmethod
    def transfer(self, node: NodeType, state_in: LatticeValue) -> LatticeValue:
        """Returns the state of a given node after transfer."""
        pass
    
    @abstractmethod
    def sources(
        self, graph: GraphProtocol[NodeType], node: NodeType
    ) -> Iterable[NodeType]:
        """Neighbors whose results flow into `node`."""
        pass
    
    @abstractmethod
    def targets(
        self, graph: GraphProtocol[NodeType], node: NodeType
    ) -> Iterable[NodeType]:
        """Neighbors to reschedule when `node`'s result changes."""
        pass
    
    @abstractmethod
    def result(
        self,
        boundary: dict[NodeType, LatticeValue],
        result: dict[NodeType, LatticeValue],
        iterations: int,
    ) -> DataflowResult[NodeType, LatticeValue]:
        """Maps boundary/result states onto in/out states."""
        pass

    def init_state(self) -> LatticeValue:
        """Initializes the lattice with the lattice's bottom operation."""
        return self.lattice.bottom()
    
    def merge_union(self, states: Iterable[LatticeValue]) -> LatticeValue:
        """Joins incoming states using the lattice's join operation."""
        states_list = list(states)
        if not states_list:
            return self.lattice.bottom()
        merged = states_list[0]
        for state in states_list[1:]:
            merged = self.lattice.join(merged, state)
        return merged
    
    def merge_intersection(self, states: Iterable[LatticeValue]) -> LatticeValue:
        """Meets incoming states using the lattice's meet operation."""
        states_list = list(states)
        if not states_list:
            return self.lattice.top()
        merged = states_list[0]
        for state in states_list[1:]:
            merged = self.lattice.meet(merged, state)
        return merged
    
    def analyze(
        self,
        graph: GraphProtocol[NodeType],
        merge_function: Callable[[Iterable[LatticeValue]], LatticeValue],
    ) -> DataflowResult[NodeType, LatticeValue]:
        """
        Runs the worklist algorithm and returns the result of the dataflow analysis.
        Steps:
        - Initializes every node's state with `init_state()`.
        - Puts all nodes in a worklist.
        - Recomputes each node from predecessor outputs.
        - If a node output changes, schedules its `targets` again.
        - Returns final states and iteration count.
        """
        nodes = list(graph.nodes())
        boundary = {node: self.init_state() for node in nodes}
        result = {node: self.init_state() for node in nodes}

        worklist = deque(nodes)
        queued = set(nodes)
        iterations = 0

        while worklist:
            node = worklist.popleft()
            queued.discard(node)
            iterations += 1
            
            srcs = list(self.sources(graph, node))
            if srcs:
                merged_input = merge_function(result[n] for n in srcs)
            else:
                merged_input = self.lattice.bottom()

            if not self.lattice.equal(boundary[node], merged_input):
                boundary[node] = merged_input

            next_result = self.transfer(node, merged_input)
            if self.lattice.equal(result[node], next_result):
                continue
            
            result[node] = next_result
            for target in self.targets(graph, node):
                if target not in queued:
                    worklist.append(target)
                    queued.add(target)

        return self.result(boundary, result, iterations)


class ForwardDataflowAnalysis(
    DataflowAnalysis[NodeType, LatticeValue], Generic[NodeType, LatticeValue]
):
    """
    Forward dataflow analysis framework.
    """
    def sources(
        self, graph: GraphProtocol[NodeType], node: NodeType
    ) -> Iterable[NodeType]:
        return graph.predecessors(node)
    
    def targets(
        self, graph: GraphProtocol[NodeType], node: NodeType
    ) -> Iterable[NodeType]:
        return graph.successors(node)
    
    def result(
        self,
        boundary: dict[NodeType, LatticeValue],
        result: dict[NodeType, LatticeValue],
        iterations: int,
    ) -> DataflowResult[NodeType, LatticeValue]:
        return DataflowResult(
            in_states=boundary, out_states=result, iterations=iterations
        )


class BackwardDataflowAnalysis(
    DataflowAnalysis[NodeType, LatticeValue], Generic[NodeType, LatticeValue]
):
    """
    Backward dataflow analysis framework.
    """
    
    def sources(
        self, graph: GraphProtocol[NodeType], node: NodeType
    ) -> Iterable[NodeType]:
        return graph.successors(node)
    
    def targets(
        self, graph: GraphProtocol[NodeType], node: NodeType
    ) -> Iterable[NodeType]:
        return graph.predecessors(node)
    
    def result(
        self,
        boundary: dict[NodeType, LatticeValue],
        result: dict[NodeType, LatticeValue],
        iterations: int,
    ) -> DataflowResult[NodeType, LatticeValue]:
        return DataflowResult(
            in_states=result, out_states=boundary, iterations=iterations
        )
    
