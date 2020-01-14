Use this code to execute style transfer tasks as Spell remote runs and download he resulting images. This code uses the Neural Style TF method used in the official Spell tutorial (https://learn.spell.run/transferring_style, which uses https://github.com/cysmith/neural-style-tf)

### Setup
1. If you don't have Python 3 installed then download and run the Anaconda 3 Python 3.7 version installer from https://www.anaconda.com/distribution.
2. Create an account at http://spell.run
3. Install the Spell command-line interface by running `pip install spell` from the terminal.
4. Log in to Spell from the terminal by running `spell login` from the terminal.
5. Download the zip file containg the code for the latest release of this app by visiting https://github.com/ebranda/spell-style-transfer/releases. Extract to a folder in a stable location on your local drive.

### Running commands
1. Place your style and content images in the respective folders in `spell-style-transfer/images/style-transfer-images/`
2. In the terminal, `cd` to the `spell-style-transfer` folder you extracted in step 5 above.
3. Run a Spell command (see below).

TODO this needs to be updated to reflect latest command syntax

Execute commands using the syntax `python run.py [command]`. The following commands are available:
* `systemcheck` - Checks that all parts of your system are up and running. Example: `python run.py systemcheck`
* `transfer [size] [style_weight] [temporal_weight]` - Run style transfer on the two images currently located in `styles` and `content` folders. Parameters are optional. Examples: 
	- `python run.py transfer`  
	- `python run.py transfer 500` 
	- `python run.py transfer 500 10000 0.02`
* `hyperparams [size] [style_weight] [temporal_weight]` - Create a grid of 9 images using various parameters. Use this to determine the correct `transfer` parameters to start with. Parameters are optional. Examples: 
	- `python run.py hyperparams`  
	- `python run.py hyperparams 500` 
	- `python run.py hyperparams 500 10000 0.02`
* `download [runId_1] [runId_2] [runId_3]` - Downloads the output file from run `[runid]` to the local folder `images/results`. You can download the outputs from multiple runs by listing the run ids as parameters. Examples: 
	- `python run.py download 54`
	- `python run.py download 54 55 56` 

