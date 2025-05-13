from typing import Optional
from oqd_compiler_infrastructure.interface import TypeReflectBaseModel
from oqd_compiler_infrastructure.rule import RewriteRule
from oqd_compiler_infrastructure.walk import Post

# AST data structures
class Expression(TypeReflectBaseModel):
    """Base class for arithmetic expressions.

    This class serves as the foundation for all expression types in the AST.
    """
    pass

class Number(Expression):
    """Represents a numeric literal.

    Attributes:
        value (float): The numeric value of the literal.
    """
    value: float

class BinaryOp(Expression):
    """Represents a binary operation.

    Attributes:
        op (str): The operator for the binary operation (e.g., '+', '-', '*', '/').
        left (Expression): The left operand of the operation.
        right (Expression): The right operand of the operation.
    """
    op: str  # '+', '-', '*', '/'
    left: Expression
    right: Expression

class Variable(Expression):
    """Represents a variable in an expression.

    Attributes:
        name (str): The name of the variable.
    """
    name: str

class AlgebraicSimplifier(RewriteRule):
    """Applies algebraic simplification rules to binary expressions.

    Rules implemented:
    - x * 1 = x
    - 1 * x = x
    - x * 0 = 0
    - 0 * x = 0
    - x + 0 = x
    - 0 + x = x
    - x - 0 = x
    """
    
    def map_BinaryOp(self, model):
        """Simplify algebraic binary operations according to defined rules.

        Args:
            model (BinaryOp): The binary operation to simplify.

        Returns:
            Expression: The simplified expression.
        """
        # Handle multiplication with 1 or 0
        # Multiplication rules: x*1 -> x, 1*x -> x, x*0 -> 0, 0*x -> 0
        if model.op == '*':
            # Check for multiplication by 1
            # x * 1 => x
            if isinstance(model.left, Number) and model.left.value == 1:
                return model.right
            # 1 * x => x
            if isinstance(model.right, Number) and model.right.value == 1:
                return model.left
            
            # Check for multiplication by 0
            # x * 0 or 0 * x => 0
            if (isinstance(model.left, Number) and model.left.value == 0) or \
               (isinstance(model.right, Number) and model.right.value == 0):
                return Number(value=0)
        
        # Handle addition/subtraction with 0
        # Addition/Subtraction rules: x+0 -> x, 0+x -> x, x-0 -> x
        elif model.op in ['+', '-']:
            if isinstance(model.right, Number) and model.right.value == 0:
                # x + 0 or x - 0 => x
                return model.left
            if model.op == '+' and isinstance(model.left, Number) and model.left.value == 0:
                # 0 + x => x
                return model.right
        
        return model

    def map_Number(self, model):
        """Return numeric literals unchanged.

        Args:
            model (Number): The number model.

        Returns:
            Number: The same number model.
        """
        # Numbers are already in simplest form
        return model
    
    def map_Variable(self, model):
        """Return variable models unchanged.

        Args:
            model (Variable): The variable model.

        Returns:
            Variable: The same variable model.
        """
        # Variables cannot be simplified further here
        return model

def print_expr(expr, prefix=""):
    """Return a readable string representation of an expression.

    Args:
        expr (Expression): The expression to format.
        prefix (str): Optional prefix for formatting.

    Returns:
        str: The formatted expression string.
    """
    # Recursively traverse the expression tree to build a string
    if isinstance(expr, Number):
        return str(expr.value)
    elif isinstance(expr, Variable):
        return expr.name
    elif isinstance(expr, BinaryOp):
        return f"({print_expr(expr.left)} {expr.op} {print_expr(expr.right)})"
    return str(expr)

def main():
    """Main function to demonstrate algebraic simplification examples."""
    # Prepare and run simplifications on several test cases
    # Create test expressions
    test_cases = [
        # x * 1
        BinaryOp(
            op='*',
            left=Variable(name='x'),
            right=Number(value=1)
        ),
        # 0 * x
        BinaryOp(
            op='*',
            left=Number(value=0),
            right=Variable(name='x')
        ),
        # (x + 0) * (y - 0)
        BinaryOp(
            op='*',
            left=BinaryOp(op='+', left=Variable(name='x'), right=Number(value=0)),
            right=BinaryOp(op='-', left=Variable(name='y'), right=Number(value=0))
        ),
        # Complex expression: ((x * 1) + (0 * y)) * (z - 0)
        BinaryOp(
            op='*',
            left=BinaryOp(
                op='+',
                left=BinaryOp(op='*', left=Variable(name='x'), right=Number(value=1)),
                right=BinaryOp(op='*', left=Number(value=0), right=Variable(name='y'))
            ),
            right=BinaryOp(op='-', left=Variable(name='z'), right=Number(value=0))
        ),
        # (x + 3) * (y - 1)
        BinaryOp(
            op='+',
            left=BinaryOp(op='+', left=Variable(name='x'), right=Number(value=3)),
            right=BinaryOp(op='-', left=Variable(name='y'), right=Number(value=1))
        )
        
    ]
    
    # Create simplifier wrapped in Post traversal
    # Post ensures we simplify from bottom-up
    simplifier = Post(AlgebraicSimplifier())
    
    # Run simplifications
    print("Algebraic Simplifications:")
    for i, expr in enumerate(test_cases, 1):
        print(f"\nTest Case {i}:")
        print(f"Original: {print_expr(expr)}")
        result = simplifier(expr)
        print(f"Simplified: {print_expr(result)}")

if __name__ == "__main__":
    main() 