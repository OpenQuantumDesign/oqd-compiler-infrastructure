In this tutorial we will implement a programming language for a calculator.

## Language Definition

<!-- prettier-ignore -->
/// admonition | Imports
    type: important

```py
from __future__ import annotations

from oqd_compiler_infrastructure import TypeReflectBaseModel
```

///

### Program

```py
class MyProgram(TypeReflectBaseModel):
    expr: MyExpr
```

### Expression

```py
class MyExpr(TypeReflectBaseModel):
    pass
```

### Integer

```py
class MyInt(MyExpr):
    value: int
```

### Operations

#### Addition

```py
class MyAdd(MyExpr):
    left: MyExpr
    right: MyExpr
```

#### Multiplication

```py
class MyMul(MyExpr):
    left: MyExpr
    right: MyExpr
```

#### Exponentiation

```py
class MyPow(MyExpr):
    left: MyExpr
    right: MyExpr
```

## Compilation

### Canonicalization

### Evaluation
