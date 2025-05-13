from typing import Optional, List
from oqd_compiler_infrastructure.interface import TypeReflectBaseModel
from oqd_compiler_infrastructure.rule import ConversionRule

# Our AST data structures (same as before)
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

# Python Code Generator
class PythonCodeGen(ConversionRule):
    """Converts an AST into Python code.

    Uses dispatch to generate Python expression strings from AST nodes.
    """
    # Generates Python expression strings by dispatching on node types
    
    def map_Number(self, model, operands=None):
        """Convert a Number model to its string representation.

        Args:
            model (Number): The number model to convert.

        Returns:
            str: The string representation of the number.
        """
        # Return the numeric value as a Python literal string
        return str(model.value)
    
    def map_BinaryOp(self, model, operands=None):
        """Convert a BinaryOp model to a Python expression string.

        Args:
            model (BinaryOp): The binary operation model to convert.

        Returns:
            str: The Python code representation of the binary operation.
        """
        # Generate code for left and right operands
        left = self(model.left)
        right = self(model.right)
        # Return the formatted binary expression
        return f"({left} {model.op} {right})"

# LaTeX Math Generator
class LaTeXCodeGen(ConversionRule):
    """Converts an AST into LaTeX math expressions.

    Uses dispatch to generate LaTeX code from AST nodes.
    """
    # Generates LaTeX code for math expressions
    
    def map_Number(self, model, operands=None):
        """Convert a Number model to its LaTeX string.

        Args:
            model (Number): The number model to convert.

        Returns:
            str: The LaTeX representation of the number.
        """
        # Return the numeric value as a LaTeX literal
        return str(model.value)
    
    def map_BinaryOp(self, model, operands=None):
        """Convert a BinaryOp model to its LaTeX representation.

        Args:
            model (BinaryOp): The binary operation model to convert.

        Returns:
            str: The LaTeX representation of the binary operation.
        """
        # Generate LaTeX for operands
        left = self(model.left)
        right = self(model.right)
        
        # Special handling for division in LaTeX
        if model.op == '/':
            return f"\\frac{{{left}}}{{{right}}}"
        # Special handling for multiplication in LaTeX
        elif model.op == '*':
            return f"{left} \\times {right}"
        else:
            return f"{left} {model.op} {right}"

# Assembly-like Instructions Generator
class AssemblyCodeGen(ConversionRule):
    """Converts an AST into assembly-like instructions.

    Generates a sequence of instructions using temporary registers.

    Attributes:
        temp_counter (int): Counter for temporary registers.
        instructions (List[str]): List of generated instructions.
    """
    # Builds a sequence of pseudo-assembly using temp registers
    
    def __init__(self):
        super().__init__()
        self.temp_counter = 0
        self.instructions = []
    
    def get_temp(self):
        """Generate a new temporary register name.

        Returns:
            str: The name of the new temporary register.
        """
        # Allocate next temporary register identifier
        self.temp_counter += 1
        return f"t{self.temp_counter}"
    
    def map_Number(self, model, operands=None):
        """Load a numeric literal into a temporary register.

        Args:
            model (Number): The number model to load.

        Returns:
            str: The temporary register holding the number.
        """
        # Create a temp, emit a LOAD instruction
        temp = self.get_temp()
        self.instructions.append(f"LOAD {temp}, {model.value}")
        return temp
    
    def map_BinaryOp(self, model, operands=None):
        """Generate instructions for a binary operation.

        Args:
            model (BinaryOp): The binary operation model.

        Returns:
            str: The temporary register holding the result.
        """
        # Recursively compute left and right into temps
        left_temp = self(model.left)
        right_temp = self(model.right)
        result_temp = self.get_temp()
        
        # Map operators to assembly instructions
        op_map = {
            '+': 'ADD',
            '-': 'SUB',
            '*': 'MUL',
            '/': 'DIV'
        }
        
        self.instructions.append(f"{op_map[model.op]} {result_temp}, {left_temp}, {right_temp}")
        return result_temp
    
    def get_program(self):
        """Return the complete assembly program as a single string.

        Returns:
            str: The concatenated assembly instructions.
        """
        # Join all instructions into a program listing
        return '\n'.join(self.instructions)

def main():
    """Main function to demonstrate multi-target code generation."""
    # Entry point: demonstrate multi-target code generators
    # Create a sample expression: (2 + 3) * (4 / 2)
    expr = BinaryOp(
        op='*',
        left=BinaryOp(op='+', left=Number(value=2), right=Number(value=3)),
        right=BinaryOp(op='/', left=Number(value=4), right=Number(value=2))
    )
    
    # Generate different representations
    python_gen = PythonCodeGen()
    latex_gen = LaTeXCodeGen()
    asm_gen = AssemblyCodeGen()
    
    python_code = python_gen(expr)
    latex_code = latex_gen(expr)
    asm_gen(expr)  # This populates the instructions
    asm_code = asm_gen.get_program()
    
    print("Original Expression:")
    print(expr)
    print("\nPython Code:")
    print(python_code)
    print("\nLaTeX Math:")
    print(latex_code)
    print("\nAssembly-like Code:")
    print(asm_code)

if __name__ == "__main__":
    main() 