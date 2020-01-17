Use this code to execute style transfer tasks as Spell remote runs and download the resulting images. 

## Setup

1. If you don't have Python 3 installed then download and run the Anaconda 3 Python 3.7 version installer from https://www.anaconda.com/distribution.
2. Create an account at http://spell.run
3. Install the Spell command-line interface by running `pip install spell` from the terminal.
4. Log in to Spell from the terminal by running `spell login` from the terminal.
5. Download the zip file containg the code for the latest release of this app by visiting https://github.com/ebranda/spell-style-transfer/releases. Extract to a folder in a stable location on your local drive.

## Running commands

### Neural Style Transfer

This code uses the Neural Style TF method used in the official Spell tutorial (https://learn.spell.run/transferring_style, which uses https://github.com/cysmith/neural-style-tf).

1. Prepare your image folders. Create a folder inside `images/style-transfer-images/`. Give this folder a descriptive name and number (e.g. `Rome-LA-01`). Inside your new folder, create a new folder called `styles` and another called `content`. Put your style and content images inside these folders.
2. Repeat step 1 with up to three image folders.
3. In the terminal, `cd` to the `spell-client` folder you extracted in step 5 above.
4. Run a Spell command (see below).

Execute commands using the syntax `python run.py [command]`.

#### Commands:


* `systemcheck` Checks that your system is up and running and can communicate with Spell.
* `st_upload` Uploads any sets of images currently in your `images/style-transfer-images/` folder.
* `st_transfer [quality=low|med|high (default=med)]` Runs style transfer on all uploaded image folders (max 3)
* `st_download [runId_1][-[runId_end]]` Downloads the output file from run `[runid]` to the local folder `images/results`. You can download the outputs from multiple runs by listing a range of run ids.

#### Examples:

*Run system check:*
```
python run.py systemcheck
```

*Upload all image folders inside images/style-transfer-images:*
```
python run.py st_upload
```

*Run style transfer on uploaded image folders at medium quality (800 iterations):*
```
python run.py st_transfer
```

*Run style transfer on uploaded image folders at high quality (2000 iterations):*
```
python run.py st_transfer high
```

*Run style transfer on uploaded image folders at low quality (400 iterations):*
```
python run.py st_transfer low
```

*Download the output file from run 54 to the local folder images/results:*
```
python run.py st_download 54
```

*Download the output files from runs 54 through 60 to the local folder images/results:*
```
python run.py st_download 54-60
```

