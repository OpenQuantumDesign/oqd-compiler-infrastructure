In this tutorial we will implement a programming language for a rudimentary calculator.

## Language Definition

In this section, we will define the algebraic data types (ADT) for the abstract syntax tree (AST) of the rudimentary calculator.

<!-- prettier-ignore -->
/// admonition | Imports
    type: important

```py
from __future__ import annotations

from oqd_compiler_infrastructure import TypeReflectBaseModel
```

///

### Program

This is the ADT that represents a program, the highest level construct of the programming language.

In this rudimentary calculator, the program only consist of a single expression.

```py
class MyProgram(TypeReflectBaseModel):
    expr: MyExpr
```

### Expression

This is the super class for mathematical expressions and consist of the operator overloading for smooth definition of an expression.

```py
class MyExpr(TypeReflectBaseModel):

    def __add__(self, other):
        return MyAdd(left=self, right=other)

    def __mul__(self, other):
        return MyMul(left=self, right=other)

    def __pow__(self, other):
        return MyPow(left=self, right=other)
```

### Integer

This is the primitive type representing an integer for the rudimentary calculator.

```py
class MyInt(MyExpr):
    value: int
```

### Operations

This is the list of supported operations for the rudimentary calculator.

/// tab | Addition

```py
class MyAdd(MyExpr):
    left: MyExpr
    right: MyExpr
```

///

/// tab | Multiplication

```py
class MyMul(MyExpr):
    left: MyExpr
    right: MyExpr
```

///

/// tab | Exponentiation

```py
class MyPow(MyExpr):
    left: MyExpr
    right: MyExpr
```

///

## Intepreter Definition

In this section, we will define a rudimentary walking tree intepreter.

<!-- prettier-ignore -->
/// admonition | Imports
    type: important

```py
from oqd_compiler_infrastructure import (
    RewriteRule,
    ConversionRule,
    Post,
    Chain,
    FixedPoint,
)
```

///

### Canonicalization

Here, we define a pass to put the expression into a canonical(standard) form that removes redundancy in our representation.

#### Rules

/// tab | Associativity

$$
\begin{align}
a + (b + c) &\rightarrow (a + b) + c \\
a * (b * c) &\rightarrow (a * b) * c
\end{align}
$$

```py

class Associativity(RewriteRule):
    def map_MyAdd(self, model):
        if isinstance(model.right, MyAdd):
            return MyAdd(
                left=MyAdd(left=model.left, right=model.right.left),
                right=model.right.right,
            )

    def map_MyMul(self, model):
        if isinstance(model.right, MyMul):
            return MyMul(
                left=MyMul(left=model.left, right=model.right.left),
                right=model.right.right,
            )
```

///

/// tab | Distributivity

$$
a * (b + c) \rightarrow a * b + a * c
$$

```py
class Distributivity(RewriteRule):
    def map_MyMul(self, model):
        if isinstance(model.left, MyAdd)):
            return MyAdd(
                left=MyMul(left=model.left.left, right=model.right),
                right=MyMul(left=model.left.right, right=model.right),
            )
        if isinstance(model.right, MyAdd):
            return MyAdd(
                left=MyMul(left=model.left, right=model.right.left),
                right=MyMul(left=model.left, right=model.right.right),
            )

```

///

#### Pass

```py
canonicalization_pass = Chain(
    FixedPoint(Post(Associativity())),
    FixedPoint(Post(Distribution())),
)
```

### Execution

Definition of the execution pass to evaluate the expression.

```py
class Execution(ConversionRule):
    def map_MyInt(self, model, operands):
        return model.value

    def map_MyAdd(self, model, operands):
        return operands["left"] + operands["right"]

    def map_MyMul(self, model, operands):
        return operands["left"] * operands["right"]

    def map_MyPow(self, model, operands):
        if operands["right"] < 0:
            raise ValueError("Negative exponents are not supported")

        return operands["left"] ** operands["right"]

    def map_MyProgram(self, model, operands):
        return operands["expr"]

execution_pass = Post(Execution())
```

### Interpreter

The canonicalization and execution passes together to form the interpreter.

```py

interpreter = Chain(
    canonicalization_pass,
    execution_pass
)
```

## Usage

An example for program definition and interpreter execution:

<!-- prettier-ignore -->
/// admonition | Example
    type: example

```py
program = MyProgram(
    expr=MyInt(value=1) + MyInt(value=2) * MyInt(value=3) ** MyInt(value=4)
)

result = interpreter(program)

```

```sh title="Terminal"
>>> 163
```

///
