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

from oqd_compiler_infrastructure import (
    LatticeBase,
    LatticeBottom,
    LatticeTop,
    MapLatticeBottom,
    MapLatticeTop,
    PowersetLattice,
    PowersetLatticeTop,
    maplattice,
)

########################################################################################


# fmt: off
class A(LatticeTop): ...
class B(A): ...
class C(A): ...
# fmt: on


class TestLatticeBase:
    @pytest.fixture
    def lattice(self):
        lattice_obj = LatticeBase[LatticeTop]()
        return lattice_obj

    @pytest.mark.parametrize(
        ("t1", "t2", "expected"),
        [
            *[(t, LatticeTop, True) for t in [LatticeBottom, A, B, C, LatticeTop]],
            *[(t, LatticeBottom, False) for t in [A, B, C, LatticeTop]],
            (LatticeBottom, LatticeBottom, True),
            *[(LatticeBottom, t, True) for t in [LatticeBottom, A, B, C, LatticeTop]],
            *[(LatticeTop, t, False) for t in [LatticeBottom, A, B, C]],
            *[(t, A, True) for t in [A, B, C]],
            (C, B, False),
            (B, C, False),
        ],
    )
    def test_leq(self, t1, t2, expected, lattice):
        assert lattice.leq(t1, t2) is expected

    @pytest.mark.parametrize(
        ("t1", "t2", "expected"),
        [
            *[
                (t, LatticeTop, LatticeTop)
                for t in [LatticeBottom, A, B, C, LatticeTop]
            ],
            *[(t, LatticeBottom, t) for t in [LatticeBottom, A, B, C, LatticeTop]],
            *[(LatticeBottom, t, t) for t in [LatticeBottom, A, B, C, LatticeTop]],
            *[
                (LatticeTop, t, LatticeTop)
                for t in [LatticeBottom, A, B, C, LatticeTop]
            ],
            *[(t, A, A) for t in [A, B, C]],
            (C, B, A),
            (B, C, A),
        ],
    )
    def test_join(self, t1, t2, expected, lattice):
        assert lattice.join(t1, t2) is expected

    @pytest.mark.parametrize(
        ("t1", "t2", "expected"),
        [
            *[(t, LatticeTop, t) for t in [LatticeBottom, A, B, C, LatticeTop]],
            *[
                (t, LatticeBottom, LatticeBottom)
                for t in [LatticeBottom, A, B, C, LatticeTop]
            ],
            *[
                (LatticeBottom, t, LatticeBottom)
                for t in [LatticeBottom, A, B, C, LatticeTop]
            ],
            *[(LatticeTop, t, t) for t in [LatticeBottom, A, B, C, LatticeTop]],
            *[(t, A, t) for t in [A, B, C]],
            (C, B, LatticeBottom),
            (B, C, LatticeBottom),
        ],
    )
    def test_meet(self, t1, t2, expected, lattice):
        assert lattice.meet(t1, t2) is expected


########################################################################################


class Testmaplattice:
    @pytest.fixture
    def lattice(self):
        return maplattice(LatticeBase[LatticeTop], default_mode="flexible")()

    def test_top(self, lattice):
        assert lattice.top() is MapLatticeTop

    def test_bottom(self, lattice):
        assert lattice.bottom() is MapLatticeBottom

    @pytest.mark.parametrize(
        ("t1", "t2", "expected"),
        [
            *[
                (t, LatticeTop, (True, LatticeTop, t))
                for t in [LatticeBottom, A, B, C, LatticeTop]
            ],
            *[
                (t, LatticeBottom, (False, t, LatticeBottom))
                for t in [A, B, C, LatticeTop]
            ],
            *[
                (LatticeBottom, t, (True, t, LatticeBottom))
                for t in [LatticeBottom, A, B, C, LatticeTop]
            ],
            *[
                (LatticeTop, t, (False, LatticeTop, t))
                for t in [LatticeBottom, A, B, C]
            ],
            *[(t, A, (True, A, t)) for t in [A, B, C]],
            (C, B, (False, A, LatticeBottom)),
            (B, C, (False, A, LatticeBottom)),
        ],
    )
    def test_embedded_element_lattice(self, t1, t2, expected, lattice):
        t1 = dict(a=t1)
        t2 = dict(a=t2)
        expected = (expected[0], dict(a=expected[1]), dict(a=expected[2]))
        assert (
            lattice.leq(t1, t2),
            lattice.join(t1, t2),
            lattice.meet(t1, t2),
        ) == expected

    @pytest.mark.parametrize(
        ("t1", "t2", "expected", "default_mode"),
        [
            ({"a": A}, {"b": B}, {"a": A, "b": B}, "flexible"),
            ({"a": A}, {"b": B}, {"a": LatticeTop, "b": LatticeTop}, "top"),
            ({"a": A}, {"b": B}, {"a": A, "b": B}, "bottom"),
            ({"a": A}, {"b": B}, {"a": LatticeTop, "b": LatticeTop}, "strict"),
        ],
    )
    def test_default_mode_join(self, t1, t2, expected, default_mode):
        lattice = maplattice(LatticeBase[LatticeTop], default_mode=default_mode)()

        assert lattice.join(t1, t2) == expected

    @pytest.mark.parametrize(
        ("t1", "t2", "expected", "default_mode"),
        [
            ({"a": A}, {"b": B}, {"a": A, "b": B}, "flexible"),
            ({"a": A}, {"b": B}, {"a": A, "b": B}, "top"),
            ({"a": A}, {"b": B}, {"a": LatticeBottom, "b": LatticeBottom}, "bottom"),
            ({"a": A}, {"b": B}, {"a": LatticeBottom, "b": LatticeBottom}, "strict"),
        ],
    )
    def test_default_mode_meet(self, t1, t2, expected, default_mode):
        lattice = maplattice(LatticeBase[LatticeTop], default_mode=default_mode)()

        assert lattice.meet(t1, t2) == expected

    @pytest.mark.parametrize(
        ("t1", "t2", "expected", "default_mode"),
        [
            ({"a": A}, {"b": B}, True, "flexible"),
            ({"a": A}, {"b": B, "a": A}, True, "flexible"),
            ({"a": A, "b": B}, {"b": B}, True, "flexible"),
            ({"a": A}, {"b": B}, False, "top"),
            ({"a": A}, {"b": B, "a": A}, False, "top"),
            ({"a": A, "b": B}, {"b": B}, True, "top"),
            ({"a": A}, {"b": B}, False, "bottom"),
            ({"a": A}, {"b": B, "a": A}, True, "bottom"),
            ({"a": A, "b": B}, {"b": B}, False, "bottom"),
            ({"a": A}, {"b": B}, False, "strict"),
            ({"a": A}, {"b": B, "a": A}, False, "strict"),
            ({"a": A, "b": B}, {"b": B}, False, "strict"),
        ],
    )
    def test_default_mode_leq(self, t1, t2, expected, default_mode):
        lattice = maplattice(LatticeBase[LatticeTop], default_mode=default_mode)()

        assert lattice.leq(t1, t2) == expected

    @pytest.mark.parametrize(
        ("t1", "t2", "expected"),
        [
            (MapLatticeBottom, MapLatticeTop, True),
            (MapLatticeTop, MapLatticeBottom, False),
            (MapLatticeTop, MapLatticeTop, True),
            (MapLatticeBottom, MapLatticeBottom, True),
            *[(MapLatticeTop, {"a{i}": A for i in range(n)}, False) for n in range(10)],
            *[({"a{i}": A for i in range(n)}, MapLatticeTop, True) for n in range(10)],
            *[
                (MapLatticeBottom, {"a{i}": A for i in range(n)}, True)
                for n in range(10)
            ],
            *[
                ({"a{i}": A for i in range(n)}, MapLatticeBottom, False)
                for n in range(10)
            ],
            ({"a1": A, "a2": B}, {"a1": B, "a2": A}, False),
            ({"a1": C, "a2": B}, {"a1": B, "a2": C}, False),
            ({"a1": C, "a2": C}, {"a1": B, "a2": B}, False),
            ({"a1": C, "a2": C}, {"a1": A, "a2": A}, True),
        ],
    )
    def test_leq(self, t1, t2, expected, lattice):
        assert lattice.leq(t1, t2) == expected

    @pytest.mark.parametrize(
        ("t1", "t2", "expected"),
        [
            (MapLatticeBottom, MapLatticeTop, MapLatticeTop),
            (MapLatticeTop, MapLatticeBottom, MapLatticeTop),
            (MapLatticeTop, MapLatticeTop, MapLatticeTop),
            (MapLatticeBottom, MapLatticeBottom, MapLatticeBottom),
            *[
                (MapLatticeTop, {"a{i}": A for i in range(n)}, MapLatticeTop)
                for n in range(10)
            ],
            *[
                ({"a{i}": A for i in range(n)}, MapLatticeTop, MapLatticeTop)
                for n in range(10)
            ],
            *[
                (
                    MapLatticeBottom,
                    {"a{i}": A for i in range(n)},
                    {"a{i}": A for i in range(n)},
                )
                for n in range(10)
            ],
            *[
                (
                    {"a{i}": A for i in range(n)},
                    MapLatticeBottom,
                    {"a{i}": A for i in range(n)},
                )
                for n in range(10)
            ],
            ({"a1": A, "a2": B}, {"a1": B, "a2": A}, {"a1": A, "a2": A}),
            ({"a1": C, "a2": B}, {"a1": B, "a2": C}, {"a1": A, "a2": A}),
            ({"a1": C, "a2": C}, {"a1": B, "a2": B}, {"a1": A, "a2": A}),
            ({"a1": C, "a2": C}, {"a1": A, "a2": A}, {"a1": A, "a2": A}),
        ],
    )
    def test_join(self, t1, t2, expected, lattice):
        assert lattice.join(t1, t2) == expected

    @pytest.mark.parametrize(
        ("t1", "t2", "expected"),
        [
            (MapLatticeBottom, MapLatticeTop, MapLatticeBottom),
            (MapLatticeTop, MapLatticeBottom, MapLatticeBottom),
            (MapLatticeTop, MapLatticeTop, MapLatticeTop),
            (MapLatticeBottom, MapLatticeBottom, MapLatticeBottom),
            *[
                (
                    MapLatticeTop,
                    {"a{i}": A for i in range(n)},
                    {"a{i}": A for i in range(n)},
                )
                for n in range(10)
            ],
            *[
                (
                    {"a{i}": A for i in range(n)},
                    MapLatticeTop,
                    {"a{i}": A for i in range(n)},
                )
                for n in range(10)
            ],
            *[
                (MapLatticeBottom, {"a{i}": A for i in range(n)}, MapLatticeBottom)
                for n in range(10)
            ],
            *[
                ({"a{i}": A for i in range(n)}, MapLatticeBottom, MapLatticeBottom)
                for n in range(10)
            ],
            ({"a1": A, "a2": B}, {"a1": B, "a2": A}, {"a1": B, "a2": B}),
            (
                {"a1": C, "a2": B},
                {"a1": B, "a2": C},
                {"a1": LatticeBottom, "a2": LatticeBottom},
            ),
            (
                {"a1": C, "a2": C},
                {"a1": B, "a2": B},
                {"a1": LatticeBottom, "a2": LatticeBottom},
            ),
            ({"a1": C, "a2": C}, {"a1": A, "a2": A}, {"a1": C, "a2": C}),
        ],
    )
    def test_meet(self, t1, t2, expected, lattice):
        assert lattice.meet(t1, t2) == expected


########################################################################################


class TestPowersetLattice:
    @pytest.fixture
    def lattice(self):
        return PowersetLattice[int]()

    @pytest.mark.parametrize(
        ("t1", "t2", "expected"),
        [
            *[(set(range(n)), set(range(n)), True) for n in range(10)],
            *[(set(range(1, n + 1)), set(range(n)), False) for n in range(1, 10)],
            *[(set(range(1, n)), set(range(n)), True) for n in range(1, 10)],
            *[(set(range(n)), set(range(10)), True) for n in range(1, 11)],
            *[(set(range(n)), set(range(10)), False) for n in range(11, 20)],
            *[(set(range(10, n)), set(range(10)), False) for n in range(11, 20)],
            *[(set(range(10)), set(range(n)), True) for n in range(11, 20)],
            *[(set(range(10)), set(range(10, n)), False) for n in range(11, 20)],
            *[(set(range(10)), set(range(n)), False) for n in range(1, 10)],
            *[(set(range(10)), set(range(n)), True) for n in range(10, 20)],
        ],
    )
    def test_leq(self, t1, t2, expected, lattice):
        assert lattice.leq(t1, t2) == expected

    @pytest.mark.parametrize(
        ("t1", "t2", "expected"),
        [
            *[(set(range(n)), set(range(n)), set(range(n))) for n in range(10)],
            *[
                (set(range(1, n + 1)), set(range(n)), set(range(n + 1)))
                for n in range(1, 10)
            ],
            *[(set(range(1, n)), set(range(n)), set(range(n))) for n in range(1, 10)],
            *[(set(range(n)), set(range(10)), set(range(10))) for n in range(1, 11)],
            *[(set(range(n)), set(range(10)), set(range(n))) for n in range(11, 20)],
            *[
                (set(range(10, n)), set(range(10)), set(range(n)))
                for n in range(11, 20)
            ],
            *[(set(range(10)), set(range(n)), set(range(n))) for n in range(11, 20)],
            *[
                (set(range(10)), set(range(10, n)), set(range(n)))
                for n in range(11, 20)
            ],
            *[(set(range(10)), set(range(n)), set(range(10))) for n in range(1, 10)],
            *[(set(range(10)), set(range(n)), set(range(n))) for n in range(10, 20)],
        ],
    )
    def test_join(self, t1, t2, expected, lattice):
        assert lattice.join(t1, t2) == expected

    @pytest.mark.parametrize(
        ("t1", "t2", "expected"),
        [
            *[(set(range(n)), set(range(n)), set(range(n))) for n in range(10)],
            *[
                (set(range(1, n + 1)), set(range(n)), set(range(1, n)))
                for n in range(1, 10)
            ],
            *[
                (set(range(1, n)), set(range(n)), set(range(1, n)))
                for n in range(1, 10)
            ],
            *[(set(range(n)), set(range(10)), set(range(n))) for n in range(1, 11)],
            *[(set(range(n)), set(range(10)), set(range(10))) for n in range(11, 20)],
            *[(set(range(10, n)), set(range(10)), set()) for n in range(11, 20)],
            *[(set(range(10)), set(range(n)), set(range(10))) for n in range(11, 20)],
            *[(set(range(10)), set(range(10, n)), set()) for n in range(11, 20)],
            *[(set(range(10)), set(range(n)), set(range(n))) for n in range(1, 10)],
            *[(set(range(10)), set(range(n)), set(range(10))) for n in range(10, 20)],
        ],
    )
    def test_meet(self, t1, t2, expected, lattice):
        assert lattice.meet(t1, t2) == expected
