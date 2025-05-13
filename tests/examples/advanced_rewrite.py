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

from typing import Optional
from oqd_compiler_infrastructure.interface import TypeReflectBaseModel
from oqd_compiler_infrastructure.rule import RewriteRule
from oqd_compiler_infrastructure.walk import Post

# AST data structures (same as before)
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

class Variable(Expression):
    """Represents a variable in an expression.

    Attributes:
        name (str): The name of the variable.
    """
    name: str

class BinaryOp(Expression):
    """Represents a binary operation.

    Attributes:
        op (str): The operator (e.g., '+', '-', '*', '/').
        left (Expression): The left operand.
        right (Expression): The right operand.
    """
    op: str  # '+', '-', '*', '/'
    left: Expression
    right: Expression

class AdvancedAlgebraicSimplifier(RewriteRule):
    """Applies advanced algebraic simplification rules.

    Rules implemented:
    - x - x = 0
    - x + (-x) = 0
    - x * x = x^2
    - (x + y) - y = x
    - Distributive law: a * (b + c) = (a * b) + (a * c)
    """
    # Implements additional algebraic identities like subtraction and distribution
    
    def map_BinaryOp(self, model):
        """Apply advanced simplification to binary operations.

        Args:
            model (BinaryOp): The binary operation to simplify.

        Returns:
            Expression: The simplified expression or original if no rule applies.
        """
        # x - x = 0
        # Rule: subtracting identical terms yields zero
        if model.op == '-' and self._expressions_equal(model.left, model.right):
            return Number(value=0)
        
        # x + (-x) = 0
        # Rule: x + (-1 * x) => 0
        if (model.op == '+' and 
            isinstance(model.right, BinaryOp) and 
            model.right.op == '*' and 
            isinstance(model.right.left, Number) and 
            model.right.left.value == -1 and 
            self._expressions_equal(model.left, model.right.right)):
            return Number(value=0)
        
        # Distributive law: a * (b + c) = (a * b) + (a * c)
        # Rule: a * (b + c) => (a*b) + (a*c)
        if (model.op == '*' and 
            isinstance(model.right, BinaryOp) and 
            model.right.op in ['+', '-']):
            # a * (b + c) -> (a * b) + (a * c)
            return BinaryOp(
                op=model.right.op,
                left=BinaryOp(op='*', left=model.left, right=model.right.left),
                right=BinaryOp(op='*', left=model.left, right=model.right.right)
            )
        
        # (x + y) - y = x
        # Rule: (x + y) - y => x
        if (model.op == '-' and 
            isinstance(model.left, BinaryOp) and 
            model.left.op == '+' and 
            self._expressions_equal(model.left.right, model.right)):
            return model.left.left
        
        return model
    
    def _expressions_equal(self, expr1, expr2):
        """Check if two expressions are structurally equal.

        Args:
            expr1 (Expression): The first expression to compare.
            expr2 (Expression): The second expression to compare.

        Returns:
            bool: True if structurally equal, False otherwise.
        """
        # Compare types and recursively compare sub-expressions
        if type(expr1) != type(expr2):
            return False
        
        if isinstance(expr1, Number):
            return expr1.value == expr2.value
        
        if isinstance(expr1, Variable):
            return expr1.name == expr2.name
        
        if isinstance(expr1, BinaryOp):
            return (expr1.op == expr2.op and 
                   self._expressions_equal(expr1.left, expr2.left) and 
                   self._expressions_equal(expr1.right, expr2.right))
        
        return False

def print_expr(expr):
    """Convert an expression into a readable string.

    Args:
        expr (Expression): The expression to format.

    Returns:
        str: A string representation of the expression.
    """
    # Convert AST nodes into parenthesized infix notation
    if isinstance(expr, Number):
        return str(expr.value)
    elif isinstance(expr, Variable):
        return expr.name
    elif isinstance(expr, BinaryOp):
        return f"({print_expr(expr.left)} {expr.op} {print_expr(expr.right)})"
    return str(expr)

def main():
    """Main function to demonstrate advanced algebraic simplification."""
    # Prepare test cases and run the AdvancedAlgebraicSimplifier
    # Create test expressions
    test_cases = [
        # x - x = 0
        BinaryOp(
            op='-',
            left=Variable(name='x'),
            right=Variable(name='x')
        ),
        
        # x + (-1 * x) = 0
        BinaryOp(
            op='+',
            left=Variable(name='x'),
            right=BinaryOp(
                op='*',
                left=Number(value=-1),
                right=Variable(name='x')
            )
        ),
        
        # a * (b + c) -> (a * b) + (a * c)
        BinaryOp(
            op='*',
            left=Variable(name='a'),
            right=BinaryOp(
                op='+',
                left=Variable(name='b'),
                right=Variable(name='c')
            )
        ),
        
        # (x + y) - y = x
        BinaryOp(
            op='-',
            left=BinaryOp(
                op='+',
                left=Variable(name='x'),
                right=Variable(name='y')
            ),
            right=Variable(name='y')
        )
    ]
    
    # Create simplifier with Post traversal
    simplifier = Post(AdvancedAlgebraicSimplifier())
    
    # Run simplifications
    print("Advanced Algebraic Simplifications:")
    for i, expr in enumerate(test_cases, 1):
        print(f"\nTest Case {i}:")
        print(f"Original: {print_expr(expr)}")
        result = simplifier(expr)
        print(f"Simplified: {print_expr(result)}")

if __name__ == "__main__":
    main() 