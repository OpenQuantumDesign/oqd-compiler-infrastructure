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

from functools import reduce
from typing import Dict, Iterable, List

import graphviz
from pydantic import Field

from .dataflow import GraphProtocol
from .interface import VisitableBaseModel
from .rule import RewriteRule

########################################################################################


class CFGBlock(VisitableBaseModel):
    """Represents one control flow node with incoming / outgoing edges and metadata."""

    register_id: int
    stmts: List[VisitableBaseModel] = Field(default_factory=list)
    preds: List[int] = Field(default_factory=list)
    succs: List[int] = Field(default_factory=list)
    exit_nodes: List[int] = Field(default_factory=list)
    edge_labels: Dict[int, str] = Field(default_factory=dict)
    tags: Dict[str, str] = Field(default_factory=dict)

    def add_succ(self, succ: int, label: str | None = None) -> None:
        if succ not in self.succs:
            self.succs.append(succ)
        if label is not None:
            self.edge_labels[succ] = label

    def add_pred(self, pred: int) -> None:
        if pred not in self.preds:
            self.preds.append(pred)

    def add_preds(self, preds: Iterable[int]) -> None:
        for pred in preds:
            self.add_pred(pred)


class CFG(VisitableBaseModel, GraphProtocol[int, CFGBlock]):
    """Defines a Control Flow Graph (CFG) with the GraphProtocol required by DataflowAnalysis."""

    blocks: Dict[int, CFGBlock] = Field(default_factory=dict)

    def __getitem__(self, idx):
        return self.blocks[idx]

    def __setitem__(self, idx, value):
        self.blocks[idx] = value

    def __delitem__(self, idx):
        del self.blocks[idx]

    def __iter__(self):
        return self.blocks.__iter__()

    def __len__(self):
        return len(self.blocks)

    def nodes(self) -> Iterable[int]:
        return self.keys()

    def predecessors(self, node: int) -> Iterable[int]:
        return self[node].preds

    def successors(self, node: int) -> Iterable[int]:
        return self[node].succs


########################################################################################


class CFGBlockAccumulator(RewriteRule):
    def _accumulate(self, block1, block2):
        self.blocks[block1].stmts += self.blocks[block2].stmts
        self.blocks[block1].succs = self.blocks[block2].succs
        self.blocks[block1].edge_labels = self.blocks[block2].edge_labels
        for succ in self.blocks[block2].succs:
            self.blocks[succ].preds[self.blocks[succ].preds.index(block2)] = block1
        self.blocks.pop(block2)

        return block1

    def map_CFG(self, model: CFG):
        self.blocks = model.blocks
        accumulated_blocks = []
        for block in self.blocks.values():
            if block.register_id == 0 or not block.succs:
                continue
            if (
                0 in block.preds
                or any(self.blocks[pred].edge_labels for pred in block.preds)
            ) and not block.edge_labels:
                acc = self(block)
                if len(acc) > 1:
                    accumulated_blocks.append(acc)

        for acc in accumulated_blocks:
            reduce(self._accumulate, acc)

        return CFG(blocks=self.blocks)

    def map_CFGBlock(self, model: CFGBlock):
        block = model
        blocks = []
        while True:
            if len(block.succs) != 1 or (len(block.preds) > 1 and block != model):
                break
            blocks.append(block.register_id)
            block = self.blocks[block.succs[0]]
        return blocks


class RelabelCFGBlocks(RewriteRule):
    def map_CFG(self, model: CFG):
        self.relabel_mapping = {
            node_label: n for n, node_label in enumerate(sorted(model.keys()))
        }

        new_blocks = {}
        for k, v in self.relabel_mapping.items():
            new_blocks[v] = self(model[k])

        model.blocks = new_blocks

        return model

    def map_CFGBlock(self, model: CFGBlock):
        model.register_id = self.relabel_mapping[model.register_id]
        model.preds = [self.relabel_mapping[pred] for pred in model.preds]
        model.succs = [self.relabel_mapping[succ] for succ in model.succs]
        model.edge_labels = {
            self.relabel_mapping[succ]: label
            for succ, label in model.edge_labels.items()
        }

        return model


########################################################################################


class CFGtoDot(RewriteRule):
    def __init__(self, *, serialize=None, max_lines=5):
        if serialize:
            self.serialize = serialize
        else:
            self.serialize = lambda x: x.__repr__()

        self.max_lines = max_lines

    def map_CFG(self, model):
        self.dot = graphviz.Digraph()

        for block in model.blocks.values():
            self(block)

        return self.dot

    def map_CFGBlock(self, model):

        if model.edge_labels:
            label = [f"Condition: {self(model.stmts[0])}"]
        else:
            label = [self(stmt) for stmt in model.stmts]

        if len(label) > self.max_lines and self.max_lines >= 0:
            label = label[: self.max_lines] + ["..."]

        self.dot.node(
            str(model.register_id),
            f"{'Branch' if model.edge_labels else ''} Block #{model.register_id}\n{'-' * 24}\n"
            + "\n".join(label),
        )

        for succ in model.succs:
            self.dot.edge(str(model.register_id), str(succ))

    def generic_map(self, model):
        return f"{self.serialize(model)}"


def cfg_to_dot(cfg: CFG, *, serialize=None, max_lines=5) -> graphviz.Digraph:
    _cfg2dot = CFGtoDot(serialize=serialize, max_lines=max_lines)

    return _cfg2dot(cfg)


########################################################################################
