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

from dataclasses import dataclass
from typing import Iterable
from oqd_compiler_infrastructure import ForwardDataflowAnalysis, Lattice


@dataclass
class SimpleGraph:
    graph_nodes: list[str]
    graph_preds: dict[str, list[str]]
    graph_succs: dict[str, list[str]]

    def nodes(self) -> Iterable[str]:
        return self.graph_nodes

    def predecessors(self, node: str) -> Iterable[str]:
        return self.graph_preds.get(node, [])

    def successors(self, node: str) -> Iterable[str]:
        return self.graph_succs.get(node, [])


class SetReachabilityLattice(Lattice[set[str]]):

    def bottom(self) -> set[str]:
        return set()

    def leq(self, t1: set[str], t2: set[str]) -> bool:
        return t1 <= t2

    def join(self, t1: set[str], t2: set[str]) -> set[str]:
        return t1 | t2

    def meet(self, t1: set[str], t2: set[str]) -> set[str]:
        return t1 & t2


class Reachability(ForwardDataflowAnalysis[str, set[str]]):
    lattice = SetReachabilityLattice()

    def transfer(self, node: str, state_in: set[str]) -> set[str]:
        return state_in | {node}


class TestForwardDataflowAnalysis:
    def test_reachability(self):
        graph = SimpleGraph(
            graph_nodes=["entry", "mid", "exit"],
            graph_preds={"mid": ["entry"], "exit": ["mid"]},
            graph_succs={"entry": ["mid"], "mid": ["exit"]},
        )
        result = Reachability().analyze(graph)

        assert result.in_states["entry"] == set()
        assert result.out_states["entry"] == {"entry"}
        assert result.out_states["mid"] == {"entry", "mid"}
        assert result.out_states["exit"] == {"entry", "mid", "exit"}
        assert result.iterations >= 3
