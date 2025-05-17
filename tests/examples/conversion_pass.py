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
from oqd_compiler_infrastructure.rule import ConversionRule

# Same data structures as before
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

# Constant folding using ConversionRule
class ConstantFoldingConversion(ConversionRule):
    """A conversion pass that folds constant expressions.

    This pass uses ConversionRule dispatch to evaluate binary operations
    with constant operands and replace them with computed values.
    """
    
    def map_Number(self, model, operands=None):
        # Numbers are terminal constants; no folding needed
        """Returns the number as is since it's already folded.

        Args:
            model (Number): The number to process.
            operands (dict, optional): The processed operands (unused).

        Returns:
            Number: The same number model.
        """
        # Numbers are already folded
        return model
    
    def map_BinaryOp(self, model, operands=None):
        # Fold binary operations: evaluate when both operands are numeric constants
        """Folds binary operations when both operands are numbers.

        Args:
            model (BinaryOp): The binary operation model.
            operands (dict, optional): Additional processed operands (unused).

        Returns:
            Number or BinaryOp: Folded number if both operands numeric, otherwise new BinaryOp.
        """
        # Recursively process operands first
        left = self(model.left)
        right = self(model.right)
        
        # If both are numbers, fold them
        if isinstance(left, Number) and isinstance(right, Number):
            if model.op == '+':
                return Number(value=left.value + right.value)
            elif model.op == '*':
                return Number(value=left.value * right.value)
            elif model.op == '-':
                return Number(value=left.value - right.value)
            elif model.op == '/':
                if right.value != 0:
                    return Number(value=left.value / right.value)
        
        # Otherwise, rebuild the BinaryOp with possibly simplified children
        return BinaryOp(op=model.op, left=left, right=right)

def main():
    """Demonstrates constant folding pass on a sample expression."""
    # Create an expression: (2 + 3) * (4 + 5)
    expr = BinaryOp(
        op='*',
        left=BinaryOp(op='+', left=Number(value=2), right=Number(value=3)),
        right=BinaryOp(op='+', left=Number(value=4), right=Number(value=5))
    )
    
    # Create and run our pass
    pass_ = ConstantFoldingConversion()
    result = pass_(expr)
    
    print(f"Original expression: {expr}")
    print(f"After constant folding: {result}")

if __name__ == "__main__":
    main() 