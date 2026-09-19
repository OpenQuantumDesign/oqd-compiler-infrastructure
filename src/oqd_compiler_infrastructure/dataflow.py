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
from functools import wraps
from typing import Any, Callable, ClassVar, Dict, Generic, Iterable

from pydantic import BaseModel, ConfigDict

from .error import DefaultErrorCollector
from .interface import GraphProtocol, NodeLabelType, NodeType
from .lattice import Lattice, LatticeValue

########################################################################################


class DataflowErrorCollector(DefaultErrorCollector):
    def report_errors(self, result: DataflowResult):
        error_report = self.__repr__().splitlines()
        error_report.insert(-1, str(result))
        error_report = "\n".join(error_report)

        if self:
            raise self._error_class(error_report)


########################################################################################


class DataflowResult(BaseModel):
    """
    The result of a dataflow analysis.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True, frozen=True)

    dataflow_analysis: DataflowAnalysis
    in_states: Dict[Any, Any]
    out_states: Dict[Any, Any]
    iterations: int

    def __str__(self):

        in_states = "\n".join(
            map(
                lambda x: "  " + x,
                [f"{node}={state}" for node, state in self.in_states.items()],
            )
        )
        out_states = "\n".join(
            map(
                lambda x: "  " + x,
                [f"{node}={state}" for node, state in self.out_states.items()],
            )
        )

        return (
            f"{' Dataflow Result ':-^100}\n"
            f"DataflowAnalysis: {self.dataflow_analysis.__class__.__name__}\n"
            f"In: \n{in_states}\n"
            f"Out: \n{out_states}\n"
            f"Iterations: {self.iterations}"
        )


class DataflowAnalysis(ABC, Generic[NodeLabelType, NodeType, LatticeValue]):
    """
    Base class that defines what every dataflow analysis must implement.
    """

    lattice: ClassVar[Lattice[LatticeValue]]

    def __init__(self, *, max_iterations=1000000):
        super().__init__()

        self._err_collector = DataflowErrorCollector()

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

    @staticmethod
    def _wrap_transfer(f: Callable):
        @wraps(f)
        def wrapped_f(self, graph, node, state_in, **kwargs):
            try:
                state_out = f(self, graph, node, state_in)
            except Exception as e:
                self._err_collector.append(e)
                state_out = state_in.copy()

            return state_out

        return wrapped_f

    @_wrap_transfer
    def wrapped_transfer(
        self,
        graph: GraphProtocol[NodeLabelType, NodeType],
        node: NodeLabelType,
        state_in: LatticeValue,
        **kwargs,
    ) -> LatticeValue:
        """Returns the state of a given node after transfer."""
        return self.transfer(graph, node, state_in, **kwargs)

    @abstractmethod
    def merge(self, states: Iterable[LatticeValue]) -> LatticeValue:
        """Merges incoming states."""

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

        boundary = initial_state.copy()
        result = initial_state.copy()

        worklist = deque(nodes)
        iterations = 0

        while worklist:
            iterations += 1

            if iterations > self.max_iterations:
                self._err_collector.append(
                    AssertionError(
                        f"DataflowAnalysis exceeded maximum number of iterations (max_iterations={self.max_iterations})"
                    )
                )
                break

            node = worklist.popleft()

            srcs = list(self.sources(graph, node))
            if srcs:
                merged_input = self.merge(result[n] for n in srcs)
            else:
                merged_input = result[node]

            if not self.lattice.equal(boundary[node], merged_input):
                boundary[node] = merged_input

            next_result = self.wrapped_transfer(graph, node, merged_input, **kwargs)
            if self.lattice.equal(result[node], next_result):
                continue

            result[node] = next_result
            for target in self.targets(graph, node):
                if target not in worklist:
                    worklist.append(target)

        result = DataflowResult(
            dataflow_analysis=self,
            in_states=boundary,
            out_states=result,
            iterations=iterations,
        )
        self._err_collector.report_errors(result)

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
