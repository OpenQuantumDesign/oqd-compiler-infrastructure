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
from oqd_compiler_infrastructure.rule import ConversionRule
from oqd_compiler_infrastructure.walk import Pre, Post, Level

# AST data structures
class Expression(TypeReflectBaseModel):
    """Base class for arithmetic expressions.

    This class serves as the foundation for all expression types in the abstract syntax tree (AST).
    It inherits from TypeReflectBaseModel to provide type reflection capabilities.
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
        left (Expression): The left operand of the binary operation.
        right (Expression): The right operand of the binary operation.
    """
    op: str  # '+', '-', '*', '/'
    left: Expression
    right: Expression

# Simpler constant folding using Post traversal
class SimpleConstantFolder(ConversionRule):
    """A simpler constant folding pass that relies on Post traversal.

    This class implements a constant folding optimization that evaluates binary operations
    with constant operands and replaces them with their computed value.

    Methods:
        map_Number(model): Returns the number as it is, since it's already folded.
        map_BinaryOp(model, operands): Evaluates the binary operation if both operands are numbers.
    """
    
    def map_Number(self, model, operands=None):
        """Returns the number as it is.

        Args:
            model (Number): The number model to be returned.

        Returns:
            Number: The same number model.
        """
        return model
    
    def map_BinaryOp(self, model, operands=None):
        """Evaluates the binary operation if both operands are numbers.

        Args:
            model (BinaryOp): The binary operation model to be evaluated.
            operands (dict, optional): The processed operands from the traversal.

        Returns:
            Number or BinaryOp: The result of the operation if both operands are numbers,
            otherwise returns a new BinaryOp with processed children.
        """
        # Called after children are processed; 'operands' contains folded results
        print(f"Visiting BinaryOp({model.op})")
        print(f"Operands: {operands}")
        
        if operands:
            # Extract folded children from operands dict
            left = operands['left']
            right = operands['right']
            
            # If both children are numeric, compute and return new Number
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
            
            return BinaryOp(op=model.op, left=left, right=right)
        # Fallback: return original model if no operands
        return model

# Debug printer to show traversal order
class DebugPrinter(ConversionRule):
    """Prints nodes as they're visited to demonstrate traversal order.

    This class is used for debugging purposes to visualize the order in which nodes
    are visited during the traversal of the AST.
    
    Attributes:
        prefix (str): A prefix string to format the output.
    """
    
    def __init__(self, prefix=""):
        super().__init__()
        self.prefix = prefix
    
    def map_Number(self, model, operands=None):
        """Prints the number being visited.

        Args:
            model (Number): The number model being visited.

        Returns:
            Number: The same number model.
        """
        # Log visiting a Number node
        print(f"{self.prefix}Visiting Number({model.value})")
        return model
    
    def map_BinaryOp(self, model, operands=None):
        """Prints the binary operation being visited.

        Args:
            model (BinaryOp): The binary operation model being visited.

        Returns:
            BinaryOp: The same binary operation model.
        """
        # Log visiting a BinaryOp node
        print(f"{self.prefix}Visiting BinaryOp({model.op})")
        return model

def main():
    """Main function to demonstrate the functionality of the AST and traversal methods."""
    # Build a sample expression tree: (2+3)*(4/2)
    expr = BinaryOp(
        op='*',
        left=BinaryOp(op='+', left=Number(value=2), right=Number(value=3)),
        right=BinaryOp(op='/', left=Number(value=4), right=Number(value=2))
    )
    
    # Pre-order: root first, then children
    print("Pre-order traversal (top-down):")
    pre_printer = Pre(DebugPrinter(prefix="  "))
    pre_printer(expr)
    
    # Post-order: children first, then root
    print("\nPost-order traversal (bottom-up):")
    post_printer = Post(DebugPrinter(prefix="  "))
    post_printer(expr)
    
    # Level-order: breadth-first traversal
    print("\nLevel-order traversal (breadth-first):")
    level_printer = Level(DebugPrinter(prefix="  "))
    level_printer(expr)
    
    # Apply post-order constant folding
    print("\nConstant folding with Post traversal:")
    folder = Post(SimpleConstantFolder())
    result = folder(expr)
    print(f"Result: {result}")

if __name__ == "__main__":
    main() 