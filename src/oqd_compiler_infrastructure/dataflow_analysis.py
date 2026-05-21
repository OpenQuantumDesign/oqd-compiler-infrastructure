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
    def nodes(self) -> Iterable[NodeType]:
        ...
    def predecessors(self, node: NodeType) -> Iterable[NodeType]:
        ...
    def successors(self, node: NodeType) -> Iterable[NodeType]:
        ...

@dataclass(frozen=True)
class DataflowResult(Generic[NodeType, StateType]):
    in_states: dict[NodeType, StateType]
    out_states: dict[NodeType, StateType]
    iterations: int


class DataflowAnalysis(ABC, Generic[NodeType, StateType]):
    @abstractmethod
    def bottom(self) -> StateType:
        pass

    @abstractmethod
    def boundary_state(self, node: NodeType) -> StateType:
        pass

    @abstractmethod
    def merge(self, states: Iterable[StateType]) -> StateType:
        pass

    @abstractmethod
    def transfer(self, node: NodeType, state_in: StateType) -> StateType:
        pass

    def states_equal(self, t1: StateType, t2: StateType) -> bool:
        return t1 == t2


class ForwardDataflowAnalysis(DataflowAnalysis[NodeType, StateType], Generic[NodeType, StateType]):
    def analyze(self, graph: GraphProtocol[NodeType]) -> DataflowResult[NodeType, StateType]:
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

