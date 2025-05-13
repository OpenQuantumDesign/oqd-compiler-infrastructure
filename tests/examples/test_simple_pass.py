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

from simple_pass import Number, BinaryOp, ConstantFoldingPass
from oqd_compiler_infrastructure.rewriter import Chain, FixedPoint

def test_basic_folding():
    """Run basic test cases for the ConstantFoldingPass."""
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

if __name__ == "__main__":
    test_basic_folding() 