import unittest
from app import utils


class TestUtils(unittest.TestCase):
    
    def test_is_integer(self):
        self.assertTrue(utils.isInteger("1"))
        self.assertFalse(utils.isInteger("1.0"))

    def test_is_numeric(self):
        self.assertTrue(utils.isNumeric("1.0"))
        self.assertTrue(utils.isNumeric("-1.0"))
        self.assertTrue(utils.isNumeric("1"))
        self.assertFalse(utils.isNumeric("1.0a"))