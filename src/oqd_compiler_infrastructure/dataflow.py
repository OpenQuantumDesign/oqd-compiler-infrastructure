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

########################################################################################

from __future__ import annotations

from abc import ABC, abstractmethod
from collections import deque
from functools import reduce
from typing import ClassVar, Dict, Generic, Iterable

from pydantic import BaseModel, ConfigDict

from .interface import GraphProtocol, NodeLabelType, NodeType
from .lattice import Lattice, LatticeValue

########################################################################################


class DataflowResult(BaseModel, Generic[NodeLabelType, NodeType, LatticeValue]):
    """
    The result of a dataflow analysis.
    """

    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    dataflow_analysis: DataflowAnalysis[NodeLabelType, NodeType, LatticeValue]
    in_states: Dict[NodeLabelType, LatticeValue]
    out_states: Dict[NodeLabelType, LatticeValue]
    iterations: int


class DataflowAnalysis(ABC, Generic[NodeLabelType, NodeType, LatticeValue]):
    """
    Base class that defines what every dataflow analysis must implement.
    """

    lattice: ClassVar[Lattice[LatticeValue]]

    def __getattr__(self, name):
        # Enable DataflowAnalysis to use methods from associated lattice directly as if it were a method of DataflowAnalysis
        return self.lattice.__getattribute__(name)

    def __init__(self, *, max_iterations=1000000):
        super().__init__()

        self.max_iterations = max_iterations

    @abstractmethod
    def sources(
        self, graph: GraphProtocol[NodeLabelType, NodeType], node: NodeLabelType
    ) -> Iterable[NodeLabelType]:
        """Neighbors whose results flow into `node`."""
        pass

    @abstractmethod
    def targets(
        self, graph: GraphProtocol[NodeLabelType, NodeType], node: NodeLabelType
    ) -> Iterable[NodeLabelType]:
        """Neighbors to reschedule when `node`'s result changes."""
        pass

    @abstractmethod
    def transfer(
        self,
        graph: GraphProtocol[NodeLabelType, NodeType],
        node: NodeLabelType,
        state_in: LatticeValue,
        **kwargs,
    ) -> LatticeValue:
        """Returns the state of a given node after transfer."""
        pass

    @abstractmethod
    def merge(self, states: Iterable[LatticeValue]) -> LatticeValue:
        """Specify merge operation for incoming states, such as lattice.merge_meet and lattice.merge_join."""

    def result(self, in_states, out_states, iterations):
        """ "Method for specifying result format for the dataflow analysis"""
        return DataflowResult(
            dataflow_analysis=self,
            in_states=in_states,
            out_states=out_states,
            iterations=iterations,
        )

    def initial_state(self, nodes) -> Dict[NodeLabelType, LatticeValue]:
        """Initial state of the nodes in the CFG."""
        return {node: self.lattice.top() for node in nodes}

    def analyze(
        self,
        graph: GraphProtocol[NodeLabelType, NodeType],
        *,
        initial_state: Dict[NodeLabelType, NodeType] = None,
        **kwargs,
    ) -> DataflowResult[NodeLabelType, LatticeValue]:
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

        if initial_state is None:
            initial_state = self.initial_state(nodes)

        in_states = initial_state.copy()
        out_states = initial_state.copy()

        worklist = deque(nodes)
        iterations = 0

        while worklist:
            iterations += 1

            if iterations > self.max_iterations:
                raise AssertionError(
                    f"DataflowAnalysis exceeded maximum number of iterations ({self.max_iterations})"
                )

            node = worklist.popleft()

            # In[n] = merge_n(Out[source(n)])
            srcs = list(self.sources(graph, node))
            if srcs:
                merged_input = self.merge(out_states[n] for n in srcs)

                if not self.lattice.equal(in_states[node], merged_input):
                    in_states[node] = merged_input

            # Out[n] = transfer(In[n])
            next_out_states = self.transfer(graph, node, in_states[node], **kwargs)
            if self.lattice.equal(out_states[node], next_out_states):
                continue

            # Out[n] changed => add target(n) to worklist
            out_states[node] = next_out_states
            for target in self.targets(graph, node):
                if target not in worklist:
                    worklist.append(target)

        result = self.result(
            in_states=in_states,
            out_states=out_states,
            iterations=iterations,
        )

        return result


class ForwardDataflowAnalysis(DataflowAnalysis[NodeLabelType, NodeType, LatticeValue]):
    """
    Forward dataflow analysis framework.
    """

    def sources(
        self, graph: GraphProtocol[NodeLabelType, NodeType], node: NodeLabelType
    ) -> Iterable[NodeLabelType]:
        return graph.predecessors(node)

    def targets(
        self, graph: GraphProtocol[NodeLabelType, NodeType], node: NodeLabelType
    ) -> Iterable[NodeLabelType]:
        return graph.successors(node)


class BackwardDataflowAnalysis(DataflowAnalysis[NodeLabelType, NodeType, LatticeValue]):
    """
    Backward dataflow analysis framework.
    """

    def sources(
        self, graph: GraphProtocol[NodeLabelType, NodeType], node: NodeLabelType
    ) -> Iterable[NodeLabelType]:
        return graph.successors(node)

    def targets(
        self, graph: GraphProtocol[NodeLabelType, NodeType], node: NodeLabelType
    ) -> Iterable[NodeLabelType]:
        return graph.predecessors(node)
