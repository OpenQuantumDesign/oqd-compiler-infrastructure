## Lattice <div style="float:right;"> [![](https://img.shields.io/badge/Implementation-7C4DFF)][oqd_compiler_infrastructure.lattice] </div>

The lattice is a mathematical object consisting of a partially ordered set of lattice values and a set of operations:

- leq a.k.a $\leq$ (comparison operator associated with the partial order) <div style="float:right;"> [![](https://img.shields.io/badge/Implementation-7C4DFF)][oqd_compiler_infrastructure.lattice.Lattice.leq] </div>
- join (evaluates the least upper bound between 2 elements of the set) <div style="float:right;"> [![](https://img.shields.io/badge/Implementation-7C4DFF)][oqd_compiler_infrastructure.lattice.Lattice.join] </div>
- meet (evaluates the greatest lower bound between 2 elements of the set) <div style="float:right;"> [![](https://img.shields.io/badge/Implementation-7C4DFF)][oqd_compiler_infrastructure.lattice.Lattice.meet] </div>

A bounded lattice has a greatest and least element in the set:

- top (greatest element) <div style="float:right;"> [![](https://img.shields.io/badge/Implementation-7C4DFF)][oqd_compiler_infrastructure.lattice.Lattice.top] </div>
- bottom (least element) <div style="float:right;"> [![](https://img.shields.io/badge/Implementation-7C4DFF)][oqd_compiler_infrastructure.lattice.Lattice.bottom] </div>

Another method provided by the implementation of lattice interface is:

- equal a.k.a $\equiv$ (comparison operator for evaluating equivalence of lattice values) <div style="float:right;"> [![](https://img.shields.io/badge/Implementation-7C4DFF)][oqd_compiler_infrastructure.lattice.Lattice.equal] </div>

/// Important

The lattice is useful when performing dataflow analysis on a program.

///

## Graph Protocol <div style="float:right;"> [![](https://img.shields.io/badge/Implementation-7C4DFF)][oqd_compiler_infrastructure.interface.GraphProtocol] </div>

The graph protocol defines a generic interface for directed graphs consisting of:

- nodes (obtains all the nodes) <div style="float:right;"> [![](https://img.shields.io/badge/Implementation-7C4DFF)][oqd_compiler_infrastructure.interface.GraphProtocol.nodes] </div>
- predecessors (obtains all predecessors of a node) <div style="float:right;"> [![](https://img.shields.io/badge/Implementation-7C4DFF)][oqd_compiler_infrastructure.interface.GraphProtocol.predecessors] </div>
- successors (obtains all successors of a node) <div style="float:right;"> [![](https://img.shields.io/badge/Implementation-7C4DFF)][oqd_compiler_infrastructure.interface.GraphProtocol.successors] </div>

This protocol can be applied on any graph object for analysis:

/// tab | CFG

The Control Flow Graph (`CFG`) is a representation of the control flow of the program consisting of nodes connected with directed edges according to the program flow.

- Blocks consisting of code (single successor)
- Branch that split the flow of the program (multiple successors)

//// html | div[style='float: right']
[![](https://img.shields.io/badge/Implementation-7C4DFF)][oqd_compiler_infrastructure.cfg.CFG]
////
///

/// tab | Etc.

Other types of graphs include:

- Dependency Graph
- IR Graph

///

## Dataflow Analysis <div style="float:right;"> [![](https://img.shields.io/badge/Implementation-7C4DFF)][oqd_compiler_infrastructure.dataflow] </div>

The `DataflowAnalysis` consist of:

- [`Lattice`](#lattice) (provides the interface for processing the abstract values (which would be the associated lattice values) of the program)
- transfer (evaluates the updated value of a program node after transfer) <div style="float:right;"> [![](https://img.shields.io/badge/Implementation-7C4DFF)][oqd_compiler_infrastructure.dataflow.DataflowAnalysis.transfer] </div>
- merge_union <div style="float:right;"> [![](https://img.shields.io/badge/Implementation-7C4DFF)][oqd_compiler_infrastructure.dataflow.DataflowAnalysis.merge_union] </div>
- merge_intersection <div style="float:right;"> [![](https://img.shields.io/badge/Implementation-7C4DFF)][oqd_compiler_infrastructure.dataflow.DataflowAnalysis.merge_intersection] </div>

Dataflow analysis can be perfomed:

/// tab | Forward
`ForwardDataflowAnalysis` analyzes the program from start to end by using a worklist algorithm with one of the merge methods defined for the [`DataflowAnalysis`](#dataflow-analysis).

//// html | div[style='float: right']
[![](https://img.shields.io/badge/Implementation-7C4DFF)][oqd_compiler_infrastructure.dataflow.ForwardDataflowAnalysis]
////
///

/// tab | Backward
`BackwardDataflowAnalysis` analyzes the program from end to start.

//// html | div[style='float: right']
[![](https://img.shields.io/badge/Implementation-7C4DFF)][oqd_compiler_infrastructure.dataflow.BackwardDataflowAnalysis]
////
///

### Dataflow Result <div style="float:right;"> [![](https://img.shields.io/badge/Implementation-7C4DFF)][oqd_compiler_infrastructure.dataflow.DataflowResult] </div>

The output of the [`DataflowAnalysis`](#dataflow-analysis) records the final `in_states`, `out_states`, and the `iterations`.

#### Examples:

/// tab | Types
We are able to implement a type lattice for our language that will be equiped to a dataflow analysis to perform type checking/inference.
The lattice values for the lattice corresponds to the set of types a value could be.
///
