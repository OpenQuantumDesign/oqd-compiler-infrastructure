from typing import Optional
from oqd_compiler_infrastructure.interface import TypeReflectBaseModel
from oqd_compiler_infrastructure.rule import RewriteRule
from oqd_compiler_infrastructure.walk import Post
from oqd_compiler_infrastructure.rewriter import Chain, FixedPoint

# AST data structures
class Expression(TypeReflectBaseModel):
    """Base class for expressions in symbolic differentiation.

    This class serves as the foundation for all expression types in the AST.
    """
    pass

class Number(Expression):
    """Represents a numeric literal.

    Attributes:
        value (float): The numeric value of the literal.
    """
    value: float

class Variable(Expression):
    """Represents a variable in an expression.

    Attributes:
        name (str): The name of the variable.
    """
    name: str

class BinaryOp(Expression):
    """Represents a binary operation.

    Attributes:
        op (str): The operator (e.g., '+', '-', '*', '/', '^').
        left (Expression): The left operand.
        right (Expression): The right operand.
    """
    op: str  # '+', '-', '*', '/', '^'

class Function(Expression):
    """Represents a mathematical function.

    Attributes:
        name (str): The name of the function (e.g., 'sin', 'cos', 'exp', 'ln').
        arg (Expression): The argument of the function.
    """
    name: str  # 'sin', 'cos', 'exp', 'ln'

class Derivative(Expression):
    """Represents a derivative operation.

    Attributes:
        expr (Expression): The expression to differentiate.
        var (str): The variable with respect to which to differentiate.
    """
    expr: Expression
    var: str  # variable to differentiate with respect to

class SymbolicDifferentiator(RewriteRule):
    """Implements symbolic differentiation rules.

    This class defines rules for differentiating constants, variables,
    arithmetic operations, exponentials, and common functions.
    """
    
    def map_Derivative(self, model):
        """Differentiate the model expression with respect to the given variable.

        Args:
            model (Derivative): The derivative model to process.

        Returns:
            Expression: The resulting differentiated expression.
        """
        # Apply differentiation rules based on expression type
        expr = model.expr
        var = model.var
        
        # Rule: d/dx(c) = 0 for constant
        # Constant rule: derivative of constant is zero
        if isinstance(expr, Number):
            return Number(value=0)
        
        # Rule: d/dx(x) = 1 for variable x
        # Variable rule: d/dx(x)=1, d/dx(y!=x)=0
        if isinstance(expr, Variable):
            if expr.name == var:
                return Number(value=1)
            return Number(value=0)
        
        # Rule: d/dx(u + v) = d/dx(u) + d/dx(v)
        # Sum rule: derivative distributes over addition/subtraction
        if isinstance(expr, BinaryOp) and expr.op in ['+', '-']:
            left_deriv = Derivative(expr=expr.left, var=var)
            right_deriv = Derivative(expr=expr.right, var=var)
            return BinaryOp(op=expr.op, left=self(left_deriv), right=self(right_deriv))
        
        # Rule: d/dx(u * v) = u * d/dx(v) + v * d/dx(u)
        # Product rule: u*v' + v*u'
        if isinstance(expr, BinaryOp) and expr.op == '*':
            u, v = expr.left, expr.right
            du = Derivative(expr=u, var=var)
            dv = Derivative(expr=v, var=var)
            term1 = BinaryOp(op='*', left=u, right=self(dv))
            term2 = BinaryOp(op='*', left=v, right=self(du))
            return BinaryOp(op='+', left=term1, right=term2)
        
        # Rule: d/dx(u^n) = n * u^(n-1) * d/dx(u)
        # Power rule: d/dx(u^n) = n*u^(n-1)*u'
        if isinstance(expr, BinaryOp) and expr.op == '^' and isinstance(expr.right, Number):
            u, n = expr.left, expr.right.value
            du = Derivative(expr=u, var=var)
            power = BinaryOp(op='^', left=u, right=Number(value=n-1))
            return BinaryOp(
                op='*',
                left=Number(value=n),
                right=BinaryOp(op='*', left=power, right=self(du))
            )
        
        # Rule: d/dx(sin(u)) = cos(u) * d/dx(u)
        # Function rule: sin
        if isinstance(expr, Function) and expr.name == 'sin':
            du = Derivative(expr=expr.arg, var=var)
            return BinaryOp(
                op='*',
                left=Function(name='cos', arg=expr.arg),
                right=self(du)
            )
        
        # Rule: d/dx(cos(u)) = -sin(u) * d/dx(u)
        # Function rule: cos
        if isinstance(expr, Function) and expr.name == 'cos':
            du = Derivative(expr=expr.arg, var=var)
            return BinaryOp(
                op='*',
                left=BinaryOp(
                    op='*',
                    left=Number(value=-1),
                    right=Function(name='sin', arg=expr.arg)
                ),
                right=self(du)
            )
        
        # Rule: d/dx(exp(u)) = exp(u) * d/dx(u)
        # Function rule: exp
        if isinstance(expr, Function) and expr.name == 'exp':
            du = Derivative(expr=expr.arg, var=var)
            return BinaryOp(op='*', left=expr, right=self(du))
        
        # Rule: d/dx(ln(u)) = d/dx(u) / u
        # Function rule: ln
        if isinstance(expr, Function) and expr.name == 'ln':
            du = Derivative(expr=expr.arg, var=var)
            return BinaryOp(op='/', left=self(du), right=expr.arg)
        
        return model

class ExpressionSimplifier(RewriteRule):
    """Simplifies expressions post-differentiation.

    This class applies algebraic simplification rules to the differentiated AST.
    """
    
    def map_BinaryOp(self, model):
        """Apply simplification rules to binary operations after differentiation.

        Args:
            model (BinaryOp): The binary operation to simplify.

        Returns:
            Expression: The simplified expression.
        """
        # First simplify the operands recursively
        model.left = self(model.left)
        model.right = self(model.right)
        
        # Simplify x^1 to x
        # Simplify power-of-one: x^1 => x
        if model.op == '^' and isinstance(model.right, Number) and model.right.value == 1:
            return model.left

        # Simplify multiplication by 1
        # Simplify multiplication by 1 and 0
        if model.op == '*':
            if isinstance(model.left, Number) and model.left.value == 1:
                return model.right
            if isinstance(model.right, Number) and model.right.value == 1:
                return model.left
            
            # Simplify multiplication by 0
            # Zero multiplication: result is zero
            if (isinstance(model.left, Number) and model.left.value == 0) or \
               (isinstance(model.right, Number) and model.right.value == 0):
                return Number(value=0)
            
            # Combine numeric coefficients
            # Combine nested numeric factors: 2*(3*x) => 6*x
            if isinstance(model.left, Number):
                if isinstance(model.right, BinaryOp) and model.right.op == '*':
                    if isinstance(model.right.left, Number):
                        # 2 * (3 * x) -> 6 * x
                        return BinaryOp(op='*',
                                      left=Number(value=model.left.value * model.right.left.value),
                                      right=model.right.right)
                    if isinstance(model.right.right, Number):
                        # 2 * (x * 3) -> 6 * x
                        return BinaryOp(op='*',
                                      left=Number(value=model.left.value * model.right.right.value),
                                      right=model.right.left)
            
            # Move all numbers to the left in multiplication chains
            if isinstance(model.right, Number):
                return BinaryOp(op='*', left=model.right, right=model.left)
        
        # Simplify addition/subtraction with 0
        # Simplify adding or subtracting zero: x+0=>x, 0+x=>x
        elif model.op in ['+', '-']:
            if isinstance(model.right, Number) and model.right.value == 0:
                return model.left
            if model.op == '+' and isinstance(model.left, Number) and model.left.value == 0:
                return model.right
        
        return model

def print_expr(expr):
    """Convert an expression into a human-readable string.

    Args:
        expr (Expression): The expression to format.

    Returns:
        str: A human-readable representation of the expression.
    """
    if isinstance(expr, Number):
        # Format number
        return str(expr.value)
    elif isinstance(expr, Variable):
        return expr.name
    elif isinstance(expr, BinaryOp):
        left = print_expr(expr.left)
        right = print_expr(expr.right)
        
        # Special handling for multiplication
        if expr.op == '*':
            # If right operand is a multiplication, merge them
            if isinstance(expr.right, BinaryOp) and expr.right.op == '*':
                terms = []
                # Add left operand
                if isinstance(expr.left, Number):
                    terms.append(str(expr.left.value))
                else:
                    terms.append(print_expr(expr.left))
                # Add right operand's parts
                if isinstance(expr.right.left, Number):
                    terms.append(str(expr.right.left.value))
                else:
                    terms.append(print_expr(expr.right.left))
                terms.append(print_expr(expr.right.right))
                return " * ".join(terms)
            
            # Simple case: just two terms
            if isinstance(expr.left, Number):
                return f"{left} * {right}"
            if not isinstance(expr.right, BinaryOp) or expr.right.op != '*':
                return f"{left} * {right}"
        
        # Default case: use parentheses
        return f"({left} {expr.op} {right})"
    elif isinstance(expr, Function):
        return f"{expr.name}({print_expr(expr.arg)})"
    elif isinstance(expr, Derivative):
        return f"d/d{expr.var}({print_expr(expr.expr)})"
    return str(expr)

def main():
    """Main function to demonstrate symbolic differentiation with simplification."""
    # Test cases for differentiation
    test_cases = [
        # d/dx(x^2)
        Derivative(
            expr=BinaryOp(
                op='^',
                left=Variable(name='x'),
                right=Number(value=2)
            ),
            var='x'
        ),
        
        # d/dx(sin(x))
        Derivative(
            expr=Function(
                name='sin',
                arg=Variable(name='x')
            ),
            var='x'
        ),
        
        # d/dx(x * sin(x))
        Derivative(
            expr=BinaryOp(
                op='*',
                left=Variable(name='x'),
                right=Function(name='sin', arg=Variable(name='x'))
            ),
            var='x'
        ),
        
        # d/dx(exp(x^2))
        Derivative(
            expr=Function(
                name='exp',
                arg=BinaryOp(
                    op='^',
                    left=Variable(name='x'),
                    right=Number(value=2)
                )
            ),
            var='x'
        ),
        
        # d/dx(sin(x^2))
        Derivative(
            expr=Function(
                name='sin',
                arg=BinaryOp(
                    op='^',
                    left=Variable(name='x'),
                    right=Number(value=2)
                )
            ),
            var='x'
        ),
        
        # d/dx(cos(x) * sin(x))
        Derivative(
            expr=BinaryOp(
                op='*',
                left=Function(name='cos', arg=Variable(name='x')),
                right=Function(name='sin', arg=Variable(name='x'))
            ),
            var='x'
        ),
        
        # d/dx(ln(x^2 + 1))
        Derivative(
            expr=Function(
                name='ln',
                arg=BinaryOp(
                    op='+',
                    left=BinaryOp(
                        op='^',
                        left=Variable(name='x'),
                        right=Number(value=2)
                    ),
                    right=Number(value=1)
                )
            ),
            var='x'
        )
    ]
    
    # Create a chain of passes:
    # 1. Differentiate the expression
    # 2. Apply simplification rules repeatedly until no more changes
    symbolic_diff_pass = Chain(
        Post(SymbolicDifferentiator()),  # First apply differentiation rules
        FixedPoint(Post(ExpressionSimplifier())),  # Apply simplification rules until no changes
    )
    
    # Run differentiation and simplification
    print("Symbolic Differentiation Examples:")
    print("=" * 50)
    for i, expr in enumerate(test_cases, 1):
        print(f"\nTest Case {i}:")
        print(f"Expression: {print_expr(expr)}")
        result = symbolic_diff_pass(expr)
        print(f"Derivative: {print_expr(result)}")
        print("-" * 30)

if __name__ == "__main__":
    main() 