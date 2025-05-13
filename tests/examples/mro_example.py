#!/usr/bin/env python3

# Demonstrates Python's Method Resolution Order (MRO) with various inheritance patterns.
def print_mro(cls):
    """Print the Method Resolution Order for a class.

    Args:
        cls (type): The class for which to print the MRO.
    """
    # Print the class name and list its MRO
    print(f"MRO for {cls.__name__}:")
    # Enumerate through the MRO tuple to display each class in order
    for i, c in enumerate(cls.__mro__):
        # Print the index and class name in the MRO
        print(f"  {i}. {c.__name__}")
    print()

# Basic inheritance example
class A:
    """Base class A with a simple method."""
    def method(self):
        """Returns a string indicating the method of class A."""
        return "A.method"

class B(A):
    """Class B that inherits from A and overrides the method."""
    def method(self):
        """Returns a string indicating the method of class B."""
        return "B.method"

class C(A):
    """Class C that inherits from A and overrides the method."""
    def method(self):
        """Returns a string indicating the method of class C."""
        return "C.method"

# Multiple inheritance
class D(B, C):
    """Class D that inherits from B and C."""
    pass

class E(C, B):  # Different order than D
    """Class E that inherits from C and B."""
    pass

# Diamond inheritance pattern
class Base:
    """Base class for diamond inheritance example."""
    def method(self):
        """Returns a string indicating the method of the Base class."""
        return "Base.method"

class Left(Base):
    """Class Left that inherits from Base and overrides the method."""
    def method(self):
        """Returns a string indicating the method of class Left."""
        return "Left.method"

class Right(Base):
    """Class Right that inherits from Base and overrides the method."""
    def method(self):
        """Returns a string indicating the method of class Right."""
        return "Right.method"

class Diamond(Left, Right):
    """Class Diamond that inherits from Left and Right."""
    pass

# Demonstrate MRO for all classes
if __name__ == "__main__":
    # Entry point: demonstrate various inheritance MRO examples
    print("Method Resolution Order (MRO) Demonstration\n")
    
    print("Basic inheritance:")
    print_mro(A)
    print_mro(B)
    print_mro(C)
    
    print("Multiple inheritance:")
    print_mro(D)
    print_mro(E)
    
    print("Diamond inheritance:")
    print_mro(Base)
    print_mro(Left)
    print_mro(Right)
    print_mro(Diamond)
    
    # Show how MRO affects method resolution
    print("Method resolution examples:")
    # Instantiate classes to demonstrate which method is called per MRO order
    d = D()
    # D inherits from B and C, so B.method is called
    e = E()
    # E inherits from C then B, so C.method is called
    diamond = Diamond()
    # Diamond inherits Left then Right, so Left.method is called
    
    print(f"D().method() calls: {d.method()}")  # Will call B.method
    print(f"E().method() calls: {e.method()}")  # Will call C.method
    print(f"Diamond().method() calls: {diamond.method()}")  # Will call Left.method 