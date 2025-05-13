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

from typing import Optional, List
from oqd_compiler_infrastructure.interface import TypeReflectBaseModel
from oqd_compiler_infrastructure.base import PassBase

# Define our expression data structures
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
        op (str): The operator (e.g., '+', '-', '*', '/').
        left (Expression): The left operand.
        right (Expression): The right operand.
    """
    op: str  # '+', '-', '*', '/'
    left: Expression
    right: Expression

# Define a simple optimization pass
class ConstantFoldingPass(PassBase):
    """A pass that folds constant expressions.

    This pass uses PassBase to recursively evaluate binary operations with constant operands
    and replace them with their computed values.
    """
    
    @property
    def children(self):
        """Returns an empty list since this pass does not have sub-passes."""
        # No child passes to apply; operates directly on nodes
        return []
    
    def map(self, model):
        """Recursively process the model and apply constant folding.

        Args:
            model (Expression): The expression to process.

        Returns:
            Expression: The processed expression after folding.
        """
        # Only handle binary operations; leave other nodes unchanged
        if isinstance(model, BinaryOp):
            # First recursively process children
            # Simplify left and right sub-expressions first
            left = self(model.left)
            right = self(model.right)
            
            # If both operands are numeric literals, compute the result
            if isinstance(left, Number) and isinstance(right, Number):
                if model.op == '+':
                    return Number(value=left.value + right.value)
                elif model.op == '*':
                    return Number(value=left.value * right.value)
                elif model.op == '-':
                    return Number(value=left.value - right.value)
                elif model.op == '/':
                    if right.value != 0:  # Avoid division by zero
                        return Number(value=left.value / right.value)
            
            # Cannot fold: return a new BinaryOp with potentially simplified children
            return BinaryOp(op=model.op, left=left, right=right)
        
        # Non-binary nodes are returned unchanged
        return model

def test_basic_folding():
    """Run basic test cases for the ConstantFoldingPass."""
    # Define and run sample expressions to verify folding
    
    # Test case 1: Simple addition (2 + 3)
    expr1 = BinaryOp(op='+', left=Number(value=2), right=Number(value=3))
    
    # Test case 2: Nested expression ((2 + 3) * (4 + 5))
    expr2 = BinaryOp(
        op='*',
        left=BinaryOp(op='+', left=Number(value=2), right=Number(value=3)),
        right=BinaryOp(op='+', left=Number(value=4), right=Number(value=5))
    )
    
    # Test case 3: Mixed constants and variables ((2 + x) * 3)
    expr3 = BinaryOp(
        op='*',
        left=BinaryOp(op='+', left=Number(value=2), right=BinaryOp(op='+', left=Number(value=1), right=Number(value=2))),
        right=Number(value=3)
    )
    
    # Create our pass
    pass_ = ConstantFoldingPass()
    
    # Run the pass on each expression
    result1 = pass_(expr1)
    result2 = pass_(expr2)
    result3 = pass_(expr3)
    
    print("Test Case 1:")
    print(f"Input: {expr1}")
    print(f"Output: {result1}")
    print()
    
    print("Test Case 2:")
    print(f"Input: {expr2}")
    print(f"Output: {result2}")
    print()
    
    print("Test Case 3:")
    print(f"Input: {expr3}")
    print(f"Output: {result3}")

# Example usage

def main():
    """Main function to demonstrate and test constant folding."""
    # Example usage: fold a sample expression and run tests
    
    # Create an expression: (2 + 3) * (4 + 5)
    expr = BinaryOp(
        op='*',
        left=BinaryOp(op='+', left=Number(value=2), right=Number(value=3)),
        right=BinaryOp(op='+', left=Number(value=4), right=Number(value=5))
    )
    
    # Create and run our pass
    pass_ = ConstantFoldingPass()
    result = pass_(expr)
    
    print(f"Original expression: {expr}")
    print(f"After constant folding: {result}")
    test_basic_folding() 


if __name__ == "__main__":
    main() 