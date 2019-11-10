import unittest
from app import utils


class TestUtils(unittest.TestCase):
    
    def test_isinteger(self):
        self.assertTrue(utils.isinteger("1"))
        self.assertFalse(utils.isinteger("1.0"))

    def test_isnumeric(self):
        self.assertTrue(utils.isnumeric("1.0"))
        self.assertTrue(utils.isnumeric("-1.0"))
        self.assertTrue(utils.isnumeric("1"))
        self.assertFalse(utils.isnumeric("1.0a"))
    
    def test_getarg(self):
        args = ["100", "1.05", "xyz", "True", "False", "1", "0"]
        self.assertEquals(
            utils.getarg(args, 0),
            "100"
        )
        self.assertEquals(
            utils.getarg(args, len(args), True),
            None
        )
        with self.assertRaises(ValueError):
            utils.getarg(args, len(args))
        with self.assertRaises(ValueError):
            utils.getarg(args, len(args), False)
        
        utils.getarg(args, 0, typecallback=utils.isinteger)
        utils.getarg(args, 1, typecallback=utils.isnumeric)
        with self.assertRaises(ValueError):
            utils.getarg(args, 2, typecallback=utils.isinteger)
        with self.assertRaises(ValueError):
            utils.getarg(args, 2, typecallback=utils.isnumeric)
        
        self.assertTrue(utils.getboolean(args, 3))
        self.assertFalse(utils.getboolean(args, 2))
        self.assertFalse(utils.getboolean(args, 4))
        self.assertTrue(utils.getboolean(args, 5))
        self.assertFalse(utils.getboolean(args, 6))
        
        self.assertEquals(
            utils.getint(args, 0),
            100
        )
        with self.assertRaises(ValueError):
            utils.getint(args, 1)
        
        
        