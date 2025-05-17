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
from pydantic import model_validator

# Base class for shapes
class Shape(TypeReflectBaseModel):
    # Base class for all shape models used in dispatch demonstration
    """Base class for shapes.

    Provides the foundation for all shape types in the system.
    """
    pass

# Different shape types
class Circle(Shape):
    """Represents a circle.

    Attributes:
        radius (float): The radius of the circle.
    """
    # Radius attribute for circle dimensions
    radius: float

class Rectangle(Shape):
    """Represents a rectangle.

    Attributes:
        width (float): The width of the rectangle.
        height (float): The height of the rectangle.
    """
    # Width and height attributes for rectangle dimensions
    width: float
    height: float

class Square(Rectangle):  # Inherits from Rectangle
    """Represents a square, a special case of a rectangle.

    Attributes:
        side (float): The side length of the square.
    """
    # Side length attribute; width/height derived in validator
    side: float
    
    @model_validator(mode='before')
    @classmethod
    def set_dimensions(cls, data):
        """Set width and height fields based on side before validation.

        Ensures squares have equal width and height based on the side attribute.
        """
        if isinstance(data, dict) and 'side' in data:
            data['width'] = data['side']
            data['height'] = data['side']
        return data

# Demonstration of dispatch
class ShapePrinter(ConversionRule):
    """Demonstrates dispatch behavior for different shapes.

    Provides handlers for various shape types and shows how inheritance affects
    method dispatch.
    """
    
    def map_Shape(self, model, operands=None):
        """Handles generic Shape models.

        Returns a default message for unknown shapes.
        """
        # Default handler for unknown shape types
        return "Unknown shape"
    
    def map_Circle(self, model, operands=None):
        """Handles Circle models.

        Returns a descriptive string including the radius.
        """
        # Return descriptive info for circle
        return f"Circle with radius {model.radius}"
    
    def map_Rectangle(self, model, operands=None):
        """Handles Rectangle models.

        Returns a descriptive string including width and height.
        """
        # Return descriptive info for rectangle dimensions
        return f"Rectangle {model.width}x{model.height}"
    
    # Note: No specific handler for Square - will use Rectangle's handler

def main():
    # Entry point: create shapes and demonstrate the dispatch mechanism
    """Main entrypoint to demonstrate shape dispatch."""
    # Create some shapes
    circle = Circle(radius=5.0)
    rectangle = Rectangle(width=4.0, height=6.0)
    square = Square(side=3.0)
    
    # Create our printer
    printer = ShapePrinter()
    
    # Demonstrate dispatch
    print("Demonstrating method dispatch:")
    print(f"Circle: {printer(circle)}")
    print(f"Rectangle: {printer(rectangle)}")
    print(f"Square: {printer(square)}  # Uses Rectangle's handler through inheritance")
    
    # Show the MRO (Method Resolution Order) for Square
    print("\nSquare's Method Resolution Order:")
    for cls in Square.__mro__:
        print(f"- {cls.__name__}")

if __name__ == "__main__":
    main() 