# Copyright 2024 Open Quantum Design

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest
from unittest_prettify.colorize import (
    colorize,
    GREEN,
    RED,
    BLUE,
    MAGENTA,
)

########################################################################################

from oqd_compiler_infrastructure import *

########################################################################################


class PrintWalkOrder(RewriteRule):
    def __init__(self):
        self.current_index = 0
        self.string = ""

    def generic_map(self, model):
        self.string += f"\n{self.current_index}: {model}"
        self.current_index += 1
        pass


class X(VisitableBaseModel):
    a: str
    b: str


class Y(TypeReflectBaseModel):
    a: str
    b: str


class N(TypeReflectBaseModel):
    pass


class A(VisitableBaseModel):
    n: N
    x: X


########################################################################################


@colorize(color=GREEN)
class TestPreWalk(unittest.TestCase):
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)

    def test_pre_list(self):
        "Test of Pre Walk on a list"
        inp = ["a", "b"]

        printer = Pre(PrintWalkOrder())

        printer(inp)
        self.assertEqual(printer.children[0].string, "\n0: ['a', 'b']\n1: a\n2: b")

    def test_pre_dict(self):
        "Test of Pre Walk on a dict"
        inp = {"a": "a", "b": "b"}

        printer = Pre(PrintWalkOrder())

        printer(inp)
        self.assertEqual(
            printer.children[0].string, "\n0: {'a': 'a', 'b': 'b'}\n1: a\n2: b"
        )

    def test_pre_VisitableBaseModel(self):
        "Test of Pre Walk on a VisitableBaseModel"
        inp = X(a="a", b="b")

        printer = Pre(PrintWalkOrder())

        printer(inp)
        self.assertEqual(printer.children[0].string, "\n0: a='a' b='b'\n1: a\n2: b")

    def test_pre_nested_list(self):
        "Test of Pre Walk on a nested list"
        inp = ["a", ["b", "c"]]

        printer = Pre(PrintWalkOrder())

        printer(inp)
        self.assertEqual(
            printer.children[0].string,
            "\n0: ['a', ['b', 'c']]\n1: a\n2: ['b', 'c']\n3: b\n4: c",
        )

    def test_reversed_pre_list(self):
        "Test of reversed Pre Walk on a list"
        inp = ["a", "b"]

        printer = Pre(PrintWalkOrder(), reverse=True)

        printer(inp)
        self.assertEqual(printer.children[0].string, "\n0: ['a', 'b']\n1: b\n2: a")

    def test_reversed_pre_dict(self):
        "Test of reversed Pre Walk on a dict"
        inp = {"a": "a", "b": "b"}

        printer = Pre(PrintWalkOrder(), reverse=True)

        printer(inp)
        self.assertEqual(
            printer.children[0].string, "\n0: {'a': 'a', 'b': 'b'}\n1: b\n2: a"
        )

    def test_reversed_pre_VisitableBaseModel(self):
        "Test of reversed Pre Walk on a VisitableBaseModel"
        inp = X(a="a", b="b")

        printer = Pre(PrintWalkOrder(), reverse=True)

        printer(inp)
        self.assertEqual(printer.children[0].string, "\n0: a='a' b='b'\n1: b\n2: a")

    def test_reversed_pre_nested_list(self):
        "Test of reversed Pre Walk on a nested list"
        inp = ["a", ["b", "c"]]

        printer = Pre(PrintWalkOrder(), reverse=True)

        printer(inp)
        self.assertEqual(
            printer.children[0].string,
            "\n0: ['a', ['b', 'c']]\n1: ['b', 'c']\n2: c\n3: b\n4: a",
        )

    def test_pre_TypeReflectBaseModel(self):
        "Test of Pre Walk on a TypeReflectBaseModel"
        inp = Y(a="a", b="b")

        printer = Pre(PrintWalkOrder())

        printer(inp)
        self.assertEqual(
            printer.children[0].string, "\n0: class_='Y' a='a' b='b'\n1: a\n2: b"
        )

    def test_reversed_pre_TypeReflectBaseModel(self):
        "Test of reversed Pre Walk on a TypeReflectBaseModel"
        inp = Y(a="a", b="b")

        printer = Pre(PrintWalkOrder(), reverse=True)

        printer(inp)
        self.assertEqual(
            printer.children[0].string, "\n0: class_='Y' a='a' b='b'\n1: b\n2: a"
        )


########################################################################################


@colorize(color=RED)
class TestPostWalk(unittest.TestCase):
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)

    def test_post_list(self):
        "Test of Post Walk on a list"
        inp = ["a", "b"]

        printer = Post(PrintWalkOrder())

        printer(inp)
        self.assertEqual(printer.children[0].string, "\n0: a\n1: b\n2: ['a', 'b']")

    def test_post_dict(self):
        "Test of Post Walk on a dict"
        inp = {"a": "a", "b": "b"}

        printer = Post(PrintWalkOrder())

        printer(inp)
        self.assertEqual(
            printer.children[0].string, "\n0: a\n1: b\n2: {'a': 'a', 'b': 'b'}"
        )

    def test_post_VisitableBaseModel(self):
        "Test of Post Walk on a VisitableBaseModel"
        inp = X(a="a", b="b")

        printer = Post(PrintWalkOrder())

        printer(inp)
        self.assertEqual(printer.children[0].string, "\n0: a\n1: b\n2: a='a' b='b'")

    def test_post_nested_list(self):
        "Test of Post Walk on a nested list"
        inp = ["a", ["b", "c"]]

        printer = Post(PrintWalkOrder())

        printer(inp)
        self.assertEqual(
            printer.children[0].string,
            "\n0: a\n1: b\n2: c\n3: ['b', 'c']\n4: ['a', ['b', 'c']]",
        )

    def test_reversed_post_list(self):
        "Test of reversed Post Walk on a list"
        inp = ["a", "b"]

        printer = Post(PrintWalkOrder(), reverse=True)

        printer(inp)
        self.assertEqual(printer.children[0].string, "\n0: b\n1: a\n2: ['a', 'b']")

    def test_reversed_post_dict(self):
        "Test of reversed Post Walk on a dict"
        inp = {"a": "a", "b": "b"}

        printer = Post(PrintWalkOrder(), reverse=True)

        printer(inp)
        self.assertEqual(
            printer.children[0].string, "\n0: b\n1: a\n2: {'a': 'a', 'b': 'b'}"
        )

    def test_reversed_post_VisitableBaseModel(self):
        "Test of reversed Post Walk on a VisitableBaseModel"
        inp = X(a="a", b="b")

        printer = Post(PrintWalkOrder(), reverse=True)

        printer(inp)
        self.assertEqual(printer.children[0].string, "\n0: b\n1: a\n2: a='a' b='b'")

    def test_reversed_post_nested_list(self):
        "Test of reversed Post Walk on a nested list"
        inp = ["a", ["b", "c"]]

        printer = Post(PrintWalkOrder(), reverse=True)

        printer(inp)
        self.assertEqual(
            printer.children[0].string,
            "\n0: c\n1: b\n2: ['b', 'c']\n3: a\n4: ['a', ['b', 'c']]",
        )

    def test_post_TypeReflectBaseModel(self):
        "Test of Post Walk on a TypeReflectBaseModel"
        inp = Y(a="a", b="b")

        printer = Post(PrintWalkOrder())

        printer(inp)
        self.assertEqual(
            printer.children[0].string, "\n0: a\n1: b\n2: class_='Y' a='a' b='b'"
        )

    def test_reversed_post_TypeReflectBaseModel(self):
        "Test of reversed Post Walk on a TypeReflectBaseModel"
        inp = Y(a="a", b="b")

        printer = Post(PrintWalkOrder(), reverse=True)

        printer(inp)
        self.assertEqual(
            printer.children[0].string, "\n0: b\n1: a\n2: class_='Y' a='a' b='b'"
        )


########################################################################################


@colorize(color=BLUE)
class TestLevelWalk(unittest.TestCase):
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)

    def test_level_list(self):
        "Test of Level Walk on a list"
        inp = ["a", "b"]

        printer = Level(PrintWalkOrder())

        printer(inp)
        self.assertEqual(printer.children[0].string, "\n0: ['a', 'b']\n1: a\n2: b")

    def test_level_dict(self):
        "Test of Level Walk on a dict"
        inp = {"a": "a", "b": "b"}

        printer = Level(PrintWalkOrder())

        printer(inp)
        self.assertEqual(
            printer.children[0].string, "\n0: {'a': 'a', 'b': 'b'}\n1: a\n2: b"
        )

    def test_level_VisitableBaseModel(self):
        "Test of Level Walk on a VisitableBaseModel"
        inp = X(a="a", b="b")

        printer = Level(PrintWalkOrder())

        printer(inp)
        self.assertEqual(printer.children[0].string, "\n0: a='a' b='b'\n1: a\n2: b")

    def test_level_nested_list(self):
        "Test of Level Walk on a nested list"
        inp = [["a", ["b", "c"]], ["d", "e"]]

        printer = Level(PrintWalkOrder())

        printer(inp)
        self.assertEqual(
            printer.children[0].string,
            "\n0: [['a', ['b', 'c']], ['d', 'e']]\n1: ['a', ['b', 'c']]\n2: ['d', 'e']\n3: a\n4: ['b', 'c']\n5: d\n6: e\n7: b\n8: c",
        )

    def test_reversed_level_list(self):
        "Test of reversed Level Walk on a list"
        inp = ["a", "b"]

        printer = Level(PrintWalkOrder(), reverse=True)

        printer(inp)
        self.assertEqual(printer.children[0].string, "\n0: ['a', 'b']\n1: b\n2: a")

    def test_reversed_level_dict(self):
        "Test of reversed Level Walk on a dict"
        inp = {"a": "a", "b": "b"}

        printer = Level(PrintWalkOrder(), reverse=True)

        printer(inp)
        self.assertEqual(
            printer.children[0].string, "\n0: {'a': 'a', 'b': 'b'}\n1: b\n2: a"
        )

    def test_reversed_level_VisitableBaseModel(self):
        "Test of reversed Level Walk on a VisitableBaseModel"
        inp = X(a="a", b="b")

        printer = Level(PrintWalkOrder(), reverse=True)

        printer(inp)
        self.assertEqual(printer.children[0].string, "\n0: a='a' b='b'\n1: b\n2: a")

    def test_reversed_level_nested_list(self):
        "Test of reversed Level Walk on a nested list"
        inp = [["a", ["b", "c"]], ["d", "e"]]

        printer = Level(PrintWalkOrder(), reverse=True)

        printer(inp)
        self.assertEqual(
            printer.children[0].string,
            "\n0: [['a', ['b', 'c']], ['d', 'e']]\n1: ['d', 'e']\n2: ['a', ['b', 'c']]\n3: e\n4: d\n5: ['b', 'c']\n6: a\n7: c\n8: b",
        )

    def test_level_TypeReflectBaseModel(self):
        "Test of Level Walk on a TypeReflectBaseModel"
        inp = Y(a="a", b="b")

        printer = Level(PrintWalkOrder())

        printer(inp)
        self.assertEqual(
            printer.children[0].string, "\n0: class_='Y' a='a' b='b'\n1: a\n2: b"
        )

    def test_reversed_level_TypeReflectBaseModel(self):
        "Test of reversed Level Walk on a TypeReflectBaseModel"
        inp = Y(a="a", b="b")

        printer = Level(PrintWalkOrder(), reverse=True)

        printer(inp)
        self.assertEqual(
            printer.children[0].string, "\n0: class_='Y' a='a' b='b'\n1: b\n2: a"
        )


########################################################################################


@colorize(color=MAGENTA)
class TestInWalk(unittest.TestCase):
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)

    def test_in_list(self):
        "Test of In Walk on a list"
        inp = ["a", "b"]

        printer = In(PrintWalkOrder())

        printer(inp)
        self.assertEqual(printer.children[0].string, "\n0: a\n1: ['a', 'b']\n2: b")

    def test_in_dict(self):
        "Test of In Walk on a dict"
        inp = {"a": "a", "b": "b"}

        printer = In(PrintWalkOrder())

        printer(inp)
        self.assertEqual(
            printer.children[0].string, "\n0: a\n1: {'a': 'a', 'b': 'b'}\n2: b"
        )

    def test_in_VisitableBaseModel(self):
        "Test of In Walk on a VisitableBaseModel"
        inp = X(a="a", b="b")

        printer = In(PrintWalkOrder())

        printer(inp)
        self.assertEqual(printer.children[0].string, "\n0: a\n1: a='a' b='b'\n2: b")

    def test_in_nested_list(self):
        "Test of In Walk on a nested list"
        inp = [["a", ["b", "c"]], ["d", "e", "f"]]

        printer = In(PrintWalkOrder())

        printer(inp)
        self.assertEqual(
            printer.children[0].string,
            "\n0: a\n1: ['a', ['b', 'c']]\n2: b\n3: ['b', 'c']\n4: c\n5: [['a', ['b', 'c']], ['d', 'e', 'f']]\n6: d\n7: e\n8: ['d', 'e', 'f']\n9: f",
        )

    def test_reversed_in_list(self):
        "Test of reversed In Walk on a list"
        inp = ["a", "b"]

        printer = In(PrintWalkOrder(), reverse=True)

        printer(inp)
        self.assertEqual(printer.children[0].string, "\n0: b\n1: ['a', 'b']\n2: a")

    def test_reversed_in_dict(self):
        "Test of reversed In Walk on a dict"
        inp = {"a": "a", "b": "b"}

        printer = In(PrintWalkOrder(), reverse=True)

        printer(inp)
        self.assertEqual(
            printer.children[0].string, "\n0: b\n1: {'a': 'a', 'b': 'b'}\n2: a"
        )

    def test_reversed_in_VisitableBaseModel(self):
        "Test of reversed In Walk on a VisitableBaseModel"
        inp = X(a="a", b="b")

        printer = In(PrintWalkOrder(), reverse=True)

        printer(inp)
        self.assertEqual(printer.children[0].string, "\n0: b\n1: a='a' b='b'\n2: a")

    def test_reversed_in_nested_list(self):
        "Test of reversed In Walk on a nested list"
        inp = [["a", ["b", "c"]], ["d", "e", "f"]]

        printer = In(PrintWalkOrder(), reverse=True)

        printer(inp)
        self.assertEqual(
            printer.children[0].string,
            "\n0: f\n1: e\n2: ['d', 'e', 'f']\n3: d\n4: [['a', ['b', 'c']], ['d', 'e', 'f']]\n5: c\n6: ['b', 'c']\n7: b\n8: ['a', ['b', 'c']]\n9: a",
        )

    def test_in_TypeReflectBaseModel(self):
        "Test of In Walk on a TypeReflectBaseModel"
        inp = Y(a="a", b="b")

        printer = In(PrintWalkOrder())

        printer(inp)
        self.assertEqual(
            printer.children[0].string, "\n0: a\n1: class_='Y' a='a' b='b'\n2: b"
        )

    def test_reversed_in_TypeReflectBaseModel(self):
        "Test of reversed In Walk on a TypeReflectBaseModel"
        inp = Y(a="a", b="b")

        printer = In(PrintWalkOrder(), reverse=True)

        printer(inp)
        self.assertEqual(
            printer.children[0].string, "\n0: b\n1: class_='Y' a='a' b='b'\n2: a"
        )

    def test_reversed_in_TypeReflectBaseModel_no_attribute(self):
        "Test of reversed In Walk on a TypeReflectBaseModel with no attribute for N"
        x = X(a="x1", b="x2")
        n = N()
        inp = A(n=n, x=x)
        printer = In(PrintWalkOrder(), reverse=True)

        printer(inp)
        self.assertEqual(
            printer.children[0].string,
            "\n0: x2\n1: a='x1' b='x2'\n2: x1\n3: n=N(class_='N') x=X(a='x1', b='x2')\n4: class_='N'",
        )
