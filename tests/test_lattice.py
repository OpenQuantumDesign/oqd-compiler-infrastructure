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

import pytest
from oqd_compiler_infrastructure import LatticeBase, Bottom, Top

class A(Top):
    pass

class B(A):
    pass

class C(A):
    pass

class TestLatticeBase:
    @pytest.fixture
    def lattice(self):
        lattice_obj = LatticeBase()
        lattice_obj.add_node(A, Top)
        lattice_obj.add_node(B, A)
        lattice_obj.add_node(C, A)
        return lattice_obj
    
    def test_leq(self, lattice):
        assert lattice.leq(A, Top)
        assert lattice.leq(B, A)
        assert lattice.leq(B, Top)
        assert lattice.leq(Bottom, B)

    def test_join(self, lattice):
        assert lattice.join(B, C) == A

    def test_meet(self, lattice):
        assert lattice.meet(B, C) == Bottom
