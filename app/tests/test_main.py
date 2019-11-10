import unittest
from app import main


class MockFilesystem(object):
    
    def __init__(self):
        self.dirs = {
            "images/style-transfer-images": 1,
            "images/style-transfer-images/styles": ["file1.jpg"],
            "images/style-transfer-images/content": ["file1.jpg"],
        }
        
    def ls(self, path):
        if path not in self.dirs: return []
        return self.dirs[path]
        
    def exists(self, path):
        return self.ls(path)


#class TestMain(unittest.TestCase):
class TestMain(object):
    
    def test_init(self):
        paths = main.paths
        self.assertEqual(paths["imagesBaseLocal"], "images/style-transfer-images")
        self.assertEqual(paths["stylesDirLocal"], "images/style-transfer-images/styles")
        self.assertEqual(paths["contentDirLocal"], "images/style-transfer-images/content")
        self.assertEqual(paths["resultsDirLocal"], "images/results")
        self.assertEqual(paths["imagesBaseRemote"], "uploads/style-transfer-images")
        self.assertEqual(paths["stylesDirRemote"], "uploads/style-transfer-images/styles")
        self.assertEqual(paths["contentDirRemote"], "uploads/style-transfer-images/content")
    
    def test_validateLocal(self):
        fs = MockFilesystem()
        paths = main.paths
        main._validateLocal(fs, paths)
        fs.dirs["images/style-transfer-images/styles"] = ["file 1.jpg"]
        with self.assertRaises(ValueError):
            main._validateLocal(fs, paths)
        fs.dirs["images/style-transfer-images/styles"] = ["file1.jpg"]
        fs.dirs["images/style-transfer-images"] = None
        with self.assertRaises(ValueError):
            main._validateLocal(fs, paths)
        fs.dirs["images/style-transfer-images"] = 1
        fs.dirs["images/style-transfer-images/styles"] = None
        with self.assertRaises(ValueError):
            main._validateLocal(fs, paths)
        fs.dirs["images/style-transfer-images/styles"] = 1
        fs.dirs["images/style-transfer-images/content"] = None
        with self.assertRaises(ValueError):
            main._validateLocal(fs, paths)
        
