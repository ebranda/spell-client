import unittest
from app import main
from app import spell


class TestSpell(unittest.TestCase):
    
    def test_flatten(self):
        params = {
            "p1": "1",
            "p2": "2",
            "p3": ["3.1", "3.2"]
        }
        flattened = spell._flatten(params)
        self.assertEqual(flattened, ["--p1", "1", "--p2", "2", "--p3", "3.1", "--p3", "3.2"])
    
    def test_transferCmd(self):
        
        paths = main.paths
        neuralArgs = []
        machineType = "K80"
        hypergrid = False
        gh = "https://github.com/cysmith/neural-style-tf"
        
        params, neuralCmd = spell._transferCmd(main.paths, "style.jpg", "content.jpg", neuralArgs, machineType, hypergrid)
        self.assertEqual(spell._flatten(params), ["--machine-type", "K80", "--github-url", gh, "--mount", paths["vggFileRemote"], "--mount", paths["stylesDirRemote"]+":styles", "--mount", paths["contentDirRemote"]+":image_input"])
        self.assertEqual(neuralCmd, "python neural_style.py --style_imgs style.jpg --content_img content.jpg")
        
        neuralArgs = ["700"]
        params, neuralCmd = spell._transferCmd(main.paths, "style.jpg", "content.jpg", neuralArgs, machineType, hypergrid)
        self.assertEqual(neuralCmd, "python neural_style.py --style_imgs style.jpg --content_img content.jpg --max_size 700")
        
        neuralArgs = ["700", "10000.0"]
        params, neuralCmd = spell._transferCmd(main.paths, "style.jpg", "content.jpg", neuralArgs, machineType, hypergrid)
        self.assertEqual(neuralCmd, "python neural_style.py --style_imgs style.jpg --content_img content.jpg --max_size 700 --style_weight 10000.0")
        
        neuralArgs = ["700", "10000.0", "0.02"]
        params, neuralCmd = spell._transferCmd(main.paths, "style.jpg", "content.jpg", neuralArgs, machineType, hypergrid)
        self.assertEqual(neuralCmd, "python neural_style.py --style_imgs style.jpg --content_img content.jpg --max_size 700 --style_weight 10000.0 --temporal_weight 0.02")
        
        machineType = "CPU"
        params, neuralCmd = spell._transferCmd(main.paths, "style.jpg", "content.jpg", neuralArgs, machineType, hypergrid)
        self.assertEqual(spell._flatten(params)[1], "CPU")
        
        hypergrid = True
        params, neuralCmd = spell._transferCmd(main.paths, "style.jpg", "content.jpg", neuralArgs, machineType, hypergrid)
        self.assertEqual(spell._flatten(params), ["--machine-type", "CPU", "--github-url", gh, "--mount", paths["vggFileRemote"], "--mount", paths["stylesDirRemote"]+":styles", "--mount", paths["contentDirRemote"]+":image_input", "--param", "STYLE_WEIGHT=1e4,1e1,1e7", "--param", "TEMPORAL_WEIGHT=2e2,2e6,2e-2"])
        self.assertEqual(neuralCmd, "python neural_style.py --style_imgs style.jpg --content_img content.jpg --max_size 700 --style_weight :STYLE_WEIGHT: --temporal_weight :TEMPORAL_WEIGHT:")
        
        
        
        