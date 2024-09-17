import unittest
from unittest_prettify.colorize import colorize, RED, GREEN, YELLOW, BLUE, MAGENTA

########################################################################################


@colorize(color=RED)
class Test(unittest.TestCase):
    def test_example(self):
        "Test example"
        assert None is None
