Compilers are composed of passes, each of which performs a specific operation on the abstract syntax tree (AST). A [`Pass`](#pass) makes use of the visitor pattern to traverse and manipulate an abstract syntax tree (AST). In our infrastructure, we separated the logic ([`Rule`](#rule)) and traversal ([`Walk`](#walk)) of the visitor pattern for better modularity. Passes can be composed, such as with a [`Rewriter`](#rewriter), to form more complex passes.

## Rule <div style="float:right;"> [![](https://img.shields.io/badge/Implementation-7C4DFF)][oqd_compiler_infrastructure.rule] </div>

Rules are used in compilers to specify a scheme for matching and manipulating nodes in an AST. The nodes may be manipulated in several ways:

- Unchanged
- Mapped to a node of the current AST (Rewrite)
- Mapped to a node of a different AST (Conversion)

/// tab | Rewrite Rule

The rewrite rule is the most basic rule that either leaves the AST unchanged or converts AST nodes between compatible nodes of the AST.

/// html | div[style='float: right']
[![](https://img.shields.io/badge/Implementation-7C4DFF)][oqd_compiler_infrastructure.rule.RewriteRule]
///
///
/// tab | Conversion Rule

The conversion rule handles the specific case where the AST nodes need to be transformed to nodes of a different AST.

<!-- prettier-ignore -->
//// admonition | Note
    type: note

Conversion requires that the AST is traversed in a topological order (children nodes converted before parent nodes) limiting the possible walks to only the [`Post`](#__tabbed_2_2) walk.
////

//// html | div[style='float: right']
[![](https://img.shields.io/badge/Implementation-7C4DFF)][oqd_compiler_infrastructure.rule.ConversionRule]
////
///

## Walk <div style="float: right;"> [![](https://img.shields.io/badge/Implementation-7C4DFF)][oqd_compiler_infrastructure.walk] </div>

Walks are the different algorithms for traversing the AST, demonstrated with the following tree:

```mermaid
    graph TD
    element0("B0"):::L2
    element1("C2"):::L3
    element2("C3"):::L3
    element3("B1"):::L2
    element4("A0"):::L1
    element5("C0"):::L3
	element6("C1"):::L3

    element3 --> element1 & element2
    element4 --> element0 & element3
    element0 --> element5 & element6

    classDef L1 stroke:#FFFFFF00,fill:#009688,color:#ffffff
    classDef L2 stroke:#FFFFFF00,fill:#00BCD4,color:#ffffff
    classDef L3 stroke:#FFFFFF00,fill:#03A9F4,color:#ffffff

```

/// tab | Pre

//// tab | Regular
$$ A0\rightarrow B0 \rightarrow C0 \rightarrow C1 \rightarrow B1 \rightarrow C2 \rightarrow C3 $$
////
//// tab | Reverse

<!-- prettier-ignore -->
///// admonition | Note
    type: note

The reverse flag triggers right to left traversal in the walk instead of the regular left to right.
/////

$$ A0\rightarrow B1 \rightarrow C3 \rightarrow C2 \rightarrow B0 \rightarrow C1 \rightarrow C0 $$
////

//// html | div[style='float: right']
[![](https://img.shields.io/badge/Implementation-7C4DFF)][oqd_compiler_infrastructure.walk.Pre]
////
///

/// tab | Post
//// tab | Regular
$$ C0\rightarrow C1 \rightarrow B0 \rightarrow C2 \rightarrow C3 \rightarrow B1 \rightarrow A0 $$
////
//// tab | Reverse

<!-- prettier-ignore -->
///// admonition | Note
    type: note

The reverse flag triggers right to left traversal in the walk instead of the regular left to right.
/////

$$ C3\rightarrow C2 \rightarrow B1 \rightarrow C1 \rightarrow C0 \rightarrow B0 \rightarrow A0 $$
////

//// html | div[style='float: right']
[![](https://img.shields.io/badge/Implementation-7C4DFF)][oqd_compiler_infrastructure.walk.Post]
////

///

/// tab | In
//// tab | Regular
$$ C0\rightarrow B0 \rightarrow C1 \rightarrow A0 \rightarrow C2 \rightarrow B1 \rightarrow C3 $$
////

//// tab | Reverse

<!-- prettier-ignore -->
///// admonition | Note
    type: note

The reverse flag triggers right to left traversal in the walk instead of the regular left to right.
/////
$$ C3\rightarrow B1 \rightarrow C2 \rightarrow A0 \rightarrow C1 \rightarrow B0 \rightarrow C0 $$
////

<!-- prettier-ignore -->
//// admonition | Note
    type: note

Due to the traversal order in the In walk, this walk is only compatible with rules that leave the AST unchanged (e.g. analysis and verification)
////

//// html | div[style='float: right']
[![](https://img.shields.io/badge/Implementation-7C4DFF)][oqd_compiler_infrastructure.walk.In]
////

///

/// tab | Level
//// tab | Regular
$$ A0\rightarrow B0 \rightarrow B1 \rightarrow C0 \rightarrow C1 \rightarrow C2 \rightarrow C3 $$
////
//// tab | Reverse

<!-- prettier-ignore -->
///// admonition | Note
    type: note

The reverse flag triggers right to left traversal in the walk instead of the regular left to right.
/////

$$ A0\rightarrow B1 \rightarrow B0 \rightarrow C3 \rightarrow C2 \rightarrow C1 \rightarrow C0 $$
////

<!-- prettier-ignore -->
//// admonition | Note
    type: note

Due to the traversal order in the Level walk, this walk is only compatible with rules that leave the AST unchanged (e.g. analysis and verification)
////

//// html | div[style='float: right']
[![](https://img.shields.io/badge/Implementation-7C4DFF)][oqd_compiler_infrastructure.walk.Level]
////

///

## Pass

A pass is an operation that processes the entire AST. Passes perform several purposes:

/// tab | Canonicalization
The canonicalization pass puts the AST into a canonical form eliminating redundancy in the AST.
///
/// tab | Analysis
The analysis pass extracts information from the AST.
///
/// tab | Verification
The verification pass checks the validity of the AST.
///
/// tab | Optimization
The optimization pass improves the performance of the program represented by the AST.
///
/// tab | Conversion
The lowering pass converts the AST to a different AST.
///
/// tab | Execution
The execution pass implements and executes the instructions of the AST to produce results (i.e. defines an interpreter for the AST).
///

The simplest form for a pass is just a [`rule`](#rule) and [`walk`](#walk) pair. These simple passes can be combined to form a more complicated pass (e.g. with a [`rewriter`](#rewriter)).

## Rewriter <div style="float: right;"> [![](https://img.shields.io/badge/Implementation-7C4DFF)][oqd_compiler_infrastructure.rewriter] </div>

A rewriter implements logic for composing and transforming passes.

/// tab | Chain

The chain rewriter sequentially applies passes to form complex passs.

/// html | div[style='float: right;']
[![](https://img.shields.io/badge/Implementation-7C4DFF)][oqd_compiler_infrastructure.rewriter.Chain]
///
///
/// tab | Fixed Point

The fixed point rewriter transforms a pass by iteratively applying the pass till convergence of the AST.

/// html | div[style='float: right;']
[![](https://img.shields.io/badge/Implementation-7C4DFF)][oqd_compiler_infrastructure.rewriter.FixedPoint]
///
///

## Lattice

The `Lattice` class in [`lattice.py`](../../src/oqd_compiler_infrastructure/lattice.py) defines a generic lattice interface with all the methods it requires. The following methods are defined:
- bottom(): Returns the bottom element of the lattice.
- leq(): Returns True if `t1 <= t2` in the lattice.
- join(): Returns the least upper bound of `t1` and `t2`.
- meet(): Returns the greatest lower bound of `t1` and `t2`.

These methods allow analysis to be done on a concrete instance of the lattice. 

The `LatticeBase` class defines a simple concrete implementation of a `Lattice`. It stores a dictionary that maps each node of the lattice to its immediate parent(s). It defines `LatticeTop` as the top element, and `LatticeBottom` as the bottom element of the lattice. This class defines the following helper methods:
- is_class_node(t): Returns True if `t` is a valid lattice node.
- add_node(t, parent): Adds a node to the lattice, by tracking the parent(s) of the node.
- atomic_ancestors(t): Returns the atomic ancestors of a given node.

These helper methods are used in the concrete implementation of the lattice operation methods: `leq`, `join`, and `meet`.

You can define your own lattice using the `LatticeBase` class.

The `MapLattice` class converts a value lattice (such as an instance of `LatticeBase`) into a lattice over `dict[str, LatticeType]` map states. Each key is tracked independently, with missing keys treated as the value lattice's `bottom()`. The `leq`, `join`, and `meet` methods are applied key-wise across the union of keys. This is useful for analyses that map variables (or labels) to lattice values.

## Dataflow

The `GraphProtocol` class in [`dataflow.py`](../../src/oqd_compiler_infrastructure/dataflow.py) defines a generic Graph Protocol interface that provides the nodes in the graph, the predecessors of a given node, and the successors of a given node. This protocol can be applied on any graph object for analysis: control flow graphs, dependency graphs, IR graphs, etc.

The `DataflowAnalysis` class requires a Lattice to implement the analysis on. This class provides a dataflow analysis framework that can be used to implement a specific dataflow analysis The following methods are defined:
- transfer(node, state_in): Returns the state of a given node after transfer.
- bottom(): Returns the default starting state for all nodes.
- merge(states): Joins incoming states using the lattice's join operation.
- states_equal(t1, t2): Returns True if two states are equal in the lattice.

The `ForwardDataflowAnalysis` class implements the forward dataflow analysis using the worklist algorithm with the `analyze` method. The output of the analysis is an instance of the `DataflowResult` class which contains the `in_states`, `out_states`, and the `iterations`.

