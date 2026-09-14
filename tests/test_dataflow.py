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
from typing import Dict, Iterable, List, Set

from oqd_compiler_infrastructure import (
    BackwardDataflowAnalysis,
    ForwardDataflowAnalysis,
    GraphProtocol,
    Lattice,
)


@dataclass
class SimpleGraph(GraphProtocol[str, str]):
    graph_nodes: List[str]
    graph_preds: Dict[str, List[str]]
    graph_succs: Dict[str, List[str]]

    def __getitem__(self, idx):
        return idx

    def __setitem__(self, idx, value):
        self.graph_nodes[self.graph_nodes.index(idx)] = value

    def __delitem__(self, idx):
        del self.graph_nodes[self.graph_nodes.index(idx)]

    def __len__(self):
        return len(self.graph_nodes)

    def __iter__(self):
        return iter({k: k for k in self.graph_nodes})

    def nodes(self) -> Iterable[str]:
        return self.graph_nodes

    def predecessors(self, node: str) -> Iterable[str]:
        return self.graph_preds.get(node, [])

    def successors(self, node: str) -> Iterable[str]:
        return self.graph_succs.get(node, [])


class SetReachabilityLattice(Lattice[Set[str]]):
    def top(self) -> Set[str]:
        return set(self.graph_nodes)

    def bottom(self) -> Set[str]:
        return set()

    def leq(self, t1: Set[str], t2: Set[str]) -> bool:
        return t1 <= t2

    def join(self, t1: Set[str], t2: Set[str]) -> Set[str]:
        return t1 | t2

    def meet(self, t1: Set[str], t2: Set[str]) -> Set[str]:
        return t1 & t2


class Reachability(ForwardDataflowAnalysis[str, str, Set[str]]):
    lattice = SetReachabilityLattice()

    def transfer(self, node: str, state_in: Set[str]) -> Set[str]:
        return state_in | {node}


class TestForwardDataflowAnalysis:
    def test_reachability(self):
        graph = SimpleGraph(
            graph_nodes=["entry", "mid", "exit"],
            graph_preds={"mid": ["entry"], "exit": ["mid"]},
            graph_succs={"entry": ["mid"], "mid": ["exit"]},
        )
        analysis = Reachability()
        result = analysis.analyze(graph, analysis.merge_union)

        assert result.in_states["entry"] == set()
        assert result.out_states["entry"] == {"entry"}
        assert result.out_states["mid"] == {"entry", "mid"}
        assert result.out_states["exit"] == {"entry", "mid", "exit"}
        assert result.iterations >= 3


class BackwardReachability(BackwardDataflowAnalysis[str, str, Set[str]]):
    lattice = SetReachabilityLattice()

    def transfer(self, node: str, state_in: Set[str]) -> Set[str]:
        return state_in | {node}


class TestBackwardDataflowAnalysis:
    def test_reachability(self):
        graph = SimpleGraph(
            graph_nodes=["entry", "mid", "exit"],
            graph_preds={"mid": ["entry"], "exit": ["mid"]},
            graph_succs={"entry": ["mid"], "mid": ["exit"]},
        )
        analysis = BackwardReachability()
        result = analysis.analyze(graph, analysis.merge_union)
        assert result.out_states["exit"] == set()
        assert result.in_states["exit"] == {"exit"}
        assert result.in_states["mid"] == {"mid", "exit"}
        assert result.in_states["entry"] == {"entry", "mid", "exit"}
        assert result.iterations >= 3
