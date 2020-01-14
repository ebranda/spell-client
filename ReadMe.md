Use this code to execute style transfer tasks as Spell remote runs and download the resulting images. 

## Setup

1. If you don't have Python 3 installed then download and run the Anaconda 3 Python 3.7 version installer from https://www.anaconda.com/distribution.
2. Create an account at http://spell.run
3. Install the Spell command-line interface by running `pip install spell` from the terminal.
4. Log in to Spell from the terminal by running `spell login` from the terminal.
5. Download the zip file containg the code for the latest release of this app by visiting https://github.com/ebranda/spell-style-transfer/releases. Extract to a folder in a stable location on your local drive.

## Running commands

###Command: Neural Style Transfer

This code uses the Neural Style TF method used in the official Spell tutorial (https://learn.spell.run/transferring_style, which uses https://github.com/cysmith/neural-style-tf).

1. Prepare your image folders. Create a folder inside `images/style-transfer-images/`. Give this folder a descriptive name and number (e.g. `Rome-LA-01`). Inside your new folder, create a new folder called `styles` and another called `content`. Put your style and content images inside these folders.
2. In the terminal, `cd` to the `spell-client` folder you extracted in step 5 above.
3. Run a Spell command (see below).


Execute commands using the syntax `python run.py [command]`. The following commands are available:

* `systemcheck` - Checks that your system is up and running and can communicate with Spell. Example: `python run.py systemcheck`
* `st_upload` - Upload any sets of images currently in your `images/style-transfer-images/` folder.
* `st_transfer [image_folder_name] [size] [style_weight] [temporal_weight]` - Run style transfer on the specified image folder. Parameters other than `img_folder_name` are optional. If you provide `all` as the image folder name, the transfer command will be automatically run on the first three uploaded folders. Examples: 
	- `python run.py st_transfer Rome-LA-01`  
	- `python run.py st_transfer Rome-LA-01 500` 
	- `python run.py st_transfer Rome-LA-01 500 10000 0.02`
	- `python run.py st_transfer all`
	- `python run.py st_transfer all 500`
* `hyperparams [size] [style_weight] [temporal_weight]` - Create a grid of 9 images using various parameters. Use this to determine the correct `transfer` parameters to start with. Parameters are optional. Examples: 
	- `python run.py st_hyperparams`  
	- `python run.py st_hyperparams 500` 
	- `python run.py st_hyperparams 500 10000 0.02`
* `st_download [runId_1][-[runId_end]]` - Downloads the output file from run `[runid]` to the local folder `images/results`. You can download the outputs from multiple runs by listing a range of run ids. Examples: 
	- `python run.py st_download 54`
	- `python run.py st_download 54-57` 

