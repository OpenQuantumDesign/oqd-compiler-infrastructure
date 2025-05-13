from typing import Optional
from oqd_compiler_infrastructure.interface import TypeReflectBaseModel
from oqd_compiler_infrastructure.rule import RewriteRule
from oqd_compiler_infrastructure.walk import Post

# Use the same Expression classes from symbolic_diff.py
# AST data structures
class Expression(TypeReflectBaseModel):
    """Base class for expressions in trigonometric simplification.

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
        op (str): The operator for the operation (e.g., '+', '-', '*', '/', '^').
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

class TrigSimplifier(RewriteRule):
    """Implements trigonometric simplification rules.

    Applies various identities and transformations for trigonometric expressions:
    - sin^2(x) + cos^2(x) = 1
    - tan(x) = sin(x)/cos(x)
    - sin(-x) = -sin(x)
    - cos(-x) = cos(x)
    - sin(x)^2 = (1 - cos(2x))/2 (if not part of sin²(x) + cos²(x))
    - cos(x)^2 = (1 + cos(2x))/2 (if not part of sin²(x) + cos²(x))
    """
    
    def walk(self, model):
        """Override walk to apply Pythagorean identity before traversal.

        Args:
            model (Expression): The expression to process.

        Returns:
            Expression: Simplified expression if identity matches, otherwise traversal result.
        """
        # If pattern matches sin^2(x)+cos^2(x), simplify to 1 immediately
        if isinstance(model, BinaryOp) and self._is_pythagorean_identity(model):
            return Number(value=1)
        return super().walk(model)
    
    def map_BinaryOp(self, model):
        """Apply double-angle transformations for trigonometric power expressions.

        Args:
            model (BinaryOp): The binary operation model.

        Returns:
            Expression: Transformed expression or original if no rule applies.
        """
        # Double-angle: sin^2(x) -> (1 - cos(2x))/2
        if self._is_trig_power(model, 'sin', 2):
            arg = self._get_trig_arg(model)
            double_arg = BinaryOp(op='*', left=Number(value=2), right=arg)
            return BinaryOp(
                op='/',
                left=BinaryOp(
                    op='-',
                    left=Number(value=1),
                    right=Function(name='cos', arg=double_arg)
                ),
                right=Number(value=2)
            )
        
        # Double-angle: cos^2(x) -> (1 + cos(2x))/2
        if self._is_trig_power(model, 'cos', 2):
            arg = self._get_trig_arg(model)
            double_arg = BinaryOp(op='*', left=Number(value=2), right=arg)
            return BinaryOp(
                op='/',
                left=BinaryOp(
                    op='+',
                    left=Number(value=1),
                    right=Function(name='cos', arg=double_arg)
                ),
                right=Number(value=2)
            )
        
        return model
    
    def _is_pythagorean_identity(self, model):
        """Check if expression matches sin^2(x) + cos^2(x) identity.

        Args:
            model (BinaryOp): The binary operation model to check.

        Returns:
            bool: True if the pattern matches, False otherwise.
        """
        # Ensure operator is addition, then check both orderings of sin^2+cos^2
        if model.op != '+':
            return False
            
        # Check both orderings: sin^2(x) + cos^2(x) and cos^2(x) + sin^2(x)
        return (
            (self._is_trig_power(model.left, 'sin', 2) and 
             self._is_trig_power(model.right, 'cos', 2) and
             self._args_equal(self._get_trig_arg(model.left), self._get_trig_arg(model.right)))
            or
            (self._is_trig_power(model.left, 'cos', 2) and 
             self._is_trig_power(model.right, 'sin', 2) and
             self._args_equal(self._get_trig_arg(model.left), self._get_trig_arg(model.right)))
        )
    
    def map_Function(self, model):
        """Simplify function expressions based on sign identities.

        Args:
            model (Function): The function model to simplify.

        Returns:
            Expression: Simplified expression or original if no rule applies.
        """
        # Identity: sin(-x) => -sin(x)
        if (model.name == 'sin' and 
            isinstance(model.arg, BinaryOp) and 
            model.arg.op == '*' and 
            isinstance(model.arg.left, Number) and 
            model.arg.left.value == -1):
            return BinaryOp(
                op='*',
                left=Number(value=-1),
                right=Function(name='sin', arg=model.arg.right)
            )
        
        # Identity: cos(-x) => cos(x)
        if (model.name == 'cos' and 
            isinstance(model.arg, BinaryOp) and 
            model.arg.op == '*' and 
            isinstance(model.arg.left, Number) and 
            model.arg.left.value == -1):
            return Function(name='cos', arg=model.arg.right)
        
        return model
    
    def _is_trig_power(self, expr, func_name, power):
        """Check if expression is a trigonometric function raised to a specified power.

        Args:
            expr (Expression): The expression to check.
            func_name (str): Name of the trigonometric function.
            power (int): The exponent power.

        Returns:
            bool: True if the expression matches the pattern.
        """
        # Match pattern: Function ^ number(power)
        return (isinstance(expr, BinaryOp) and 
                expr.op == '^' and 
                isinstance(expr.left, Function) and 
                expr.left.name == func_name and
                isinstance(expr.right, Number) and 
                expr.right.value == power)
    
    def _get_trig_arg(self, expr):
        """Extract the argument from a trigonometric power expression.

        Args:
            expr (BinaryOp): The trigonometric power expression.

        Returns:
            Expression: The argument of the function.
        """
        # The function node is expr.left; return its argument
        return expr.left.arg
    
    def _args_equal(self, arg1, arg2):
        """Check if two expression arguments are structurally equal.

        Args:
            arg1 (Expression): The first argument to compare.
            arg2 (Expression): The second argument to compare.

        Returns:
            bool: True if the arguments are equal, False otherwise.
        """
        # Perform recursive structural comparison of arguments
        if type(arg1) != type(arg2):
            return False
        
        if isinstance(arg1, Number):
            return arg1.value == arg2.value
        elif isinstance(arg1, Variable):
            return arg1.name == arg2.name
        elif isinstance(arg1, BinaryOp):
            return (arg1.op == arg2.op and 
                   self._args_equal(arg1.left, arg2.left) and 
                   self._args_equal(arg1.right, arg2.right))
        elif isinstance(arg1, Function):
            return (arg1.name == arg2.name and 
                   self._args_equal(arg1.arg, arg2.arg))
        
        return False

def print_expr(expr):
    """Convert an expression to a human-readable string.

    Args:
        expr (Expression): The expression to print.

    Returns:
        str: A readable string representation of the expression.
    """
    # Pretty-print literals, binary ops, functions, and derivatives
    if isinstance(expr, Number):
        return str(expr.value)
    elif isinstance(expr, Variable):
        return expr.name
    elif isinstance(expr, BinaryOp):
        return f"({print_expr(expr.left)} {expr.op} {print_expr(expr.right)})"
    elif isinstance(expr, Function):
        return f"{expr.name}({print_expr(expr.arg)})"
    return str(expr)

def main():
    """Main function to demonstrate trigonometric simplification examples."""
    # Prepare test cases and apply simplifier to each
    test_cases = [
        # sin^2(x) + cos^2(x) = 1
        BinaryOp(
            op='+',
            left=BinaryOp(
                op='^',
                left=Function(name='sin', arg=Variable(name='x')),
                right=Number(value=2)
            ),
            right=BinaryOp(
                op='^',
                left=Function(name='cos', arg=Variable(name='x')),
                right=Number(value=2)
            )
        ),
        
        # cos^2(x) + sin^2(x) = 1 (reverse order)
        BinaryOp(
            op='+',
            left=BinaryOp(
                op='^',
                left=Function(name='cos', arg=Variable(name='x')),
                right=Number(value=2)
            ),
            right=BinaryOp(
                op='^',
                left=Function(name='sin', arg=Variable(name='x')),
                right=Number(value=2)
            )
        ),
        
        # sin^2(x) alone should use double angle formula
        BinaryOp(
            op='^',
            left=Function(name='sin', arg=Variable(name='x')),
            right=Number(value=2)
        ),
        
        # sin(-x) = -sin(x)
        Function(
            name='sin',
            arg=BinaryOp(
                op='*',
                left=Number(value=-1),
                right=Variable(name='x')
            )
        )
    ]
    
    # Create simplifier that checks for Pythagorean identity first
    simplifier = TrigSimplifier()
    
    # Run simplifications
    print("Trigonometric Simplification Examples:")
    for i, expr in enumerate(test_cases, 1):
        print(f"\nTest Case {i}:")
        print(f"Original: {print_expr(expr)}")
        # First try to match Pythagorean identity
        if isinstance(expr, BinaryOp) and simplifier._is_pythagorean_identity(expr):
            result = Number(value=1)
        else:
            # If not Pythagorean identity, apply other transformations
            result = Post(simplifier)(expr)
        print(f"Simplified: {print_expr(result)}")

if __name__ == "__main__":
    main() 