import unittest

loader = unittest.TestLoader()
suite = loader.discover("./", pattern="test_*.py")
unittest.TextTestRunner().run(suite)