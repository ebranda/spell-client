import _thread
import time
from app import spell
from app import utils
from app import filesystem as localfs


paths = {
    "imagesLocal": localfs.filepath("images"),
    "datasetLocal": localfs.filepath("images", "pix2pix-dataset"),
    "datasetLocalA": localfs.filepath("images", "pix2pix-dataset", "A"),
    "datasetLocalB": localfs.filepath("images", "pix2pix-dataset", "B"),
    "datasetRemote": "uploads/pix2pix-dataset"
}

if not localfs.exists(paths["imagesLocal"]): 
    localfs.mkdir(paths["imagesLocal"])
if not localfs.exists(paths["datasetLocal"]): 
    localfs.mkdir(paths["datasetLocal"])
if not localfs.exists(paths["datasetLocalA"]): 
    localfs.mkdir(paths["datasetLocalA"])
if not localfs.exists(paths["datasetLocalB"]): 
    localfs.mkdir(paths["datasetLocalB"])


def upload(machineType="CPU"):
    """
    Runs a pix2pix image upload and processing job on Spell.
    
    """
    print("Preparing to upload images...")
    
    # Run validation
    if localfs.isEmpty(paths["datasetLocalA"]):
        raise RuntimeError("Missing images in dataset folder A")
    if localfs.isEmpty(paths["datasetLocalB"]):
        raise RuntimeError("Missing images in dataset folder B")
    def validateFilenames(names):
        for n in names:
            if " " in n:
                raise ValueError("Image file names cannot contain spaces.") # TODO add non-alphanumeric character checking
    validateFilenames(localfs.ls(paths["datasetLocalA"]))
    validateFilenames(localfs.ls(paths["datasetLocalB"]))
    spell.validateMachineType(machineType)
    
    # Upload
    print("Uploading. Please wait...")
    spell.upload(paths["datasetLocal"], paths["datasetRemote"])
    time.sleep(5) # Wait for upload directory to be available for next step
    
    # Create image pairs
    print("Processing images. Please wait...")
    cmd = "python tools/process.py --input_dir dataset/A --b_dir dataset/B --operation combine --output_dir dataset/C"
    run = spell.client.runs.new(
        command = cmd, 
        machine_type = machineType, 
        github_url = "https://github.com/affinelayer/pix2pix-tensorflow.git",
        attached_resources = {
            paths["datasetRemote"]: "dataset"
        }
    )
    spell.labelRun(run, "Pix2Pix image processing")
    spell.waitUntilComplete(run)
    runId = spell.getId(run)
    localfs.cacheSet("pix2pixDatasetRunId", runId)
    print("Done.")
    


def setDatasetRunId(pix2pixArgs):
    """
    Updates the dataset run id in the cache. 
    
    """
    if not pix2pixArgs:
        raise ValueError("Run id required")
    if not utils.isInteger(pix2pixArgs[0]):
        raise ValueError("Run id must be an integer")
    localfs.cacheSet("pix2pixDatasetRunId", runId)
        

def train(pix2pixArgs, machineType="K80"):
    """
    Runs a pix2pix model training job on Spell. See https://learn.spell.run/pix2pix
    
    """
    print ("Preparing to train pix2pix model...")
    
    # Run validation
    maxEpochs = 200
    if pix2pixArgs:
        if not utils.isInteger(pix2pixArgs[0]):
            raise ValueError("max_epochs parameter must be an integer")
        maxEpochs = int(pix2pixArgs[0])
    spell.validateMachineType(machineType)
    
    # Build the spell run command (from https://learn.spell.run/pix2pix but using remote git repo)
    runId = localfs.cacheGet("pix2pixDatasetRunId")
    if not runId:
        raise RuntimeError("No dataset run ID found. Use the dataset run id command to set it first.")
    pix2pixCmd = "python pix2pix.py --mode train \
                --max_epochs {} --which_direction BtoA \
                --input_dir dataset --output_dir output --display_freq 50"
    print ("Training...")
    run = spell.client.runs.new(
        command = pix2pixCmd.format(maxEpochs), 
        machine_type = machineType, 
        github_url = "https://github.com/affinelayer/pix2pix-tensorflow.git",
        attached_resources = {
            "runs/{}/dataset/C".format(runId): "dataset"
        }
    )
    spell.labelRun(run, "Pix2Pix train")
    spell.waitUntilRunning(run)
    runId = spell.getId(run)
    localfs.cacheSet("pix2pixTrainingRunId", runId)
    print(spell.getRunStartedMessage(run))


def export(args, machineType="CPU"):
    """
    Runs a pix2pix model export job on Spell. Automatically downloads
    the finished model to the local "models" directory.
    
    """
    if args:
        if not utils.isInteger(args[0]):
            raise ValueError("Run id parameter must be an integer")
        runId = args[0]
        localfs.cacheSet("pix2pixTrainingRunId", runId)
    else:
        runId = localfs.cacheGet("pix2pixTrainingRunId")
    pix2pixCmd1 = "python pix2pix.py --mode export --output_dir output/ --checkpoint input_model/ --which_direction BtoA"
    pix2pixCmd2 = "python server/tools/export-checkpoint.py --checkpoint output --output_file output/model.pict"
    pix2pixCmd = pix2pixCmd1+";"+pix2pixCmd2
    print ("Exporting. Please wait...")
    run = spell.client.runs.new(
        command = pix2pixCmd, 
        machine_type = machineType, 
        github_url = "https://github.com/affinelayer/pix2pix-tensorflow.git",
        attached_resources = {
            "runs/{}/output".format(runId): "input_model"
        }
    )
    spell.labelRun(run, "Pix2Pix export")
    spell.waitUntilComplete(run)
    print("Export complete. Downloading model pict file...")
    run.cp("output/model.pict", localfs.filepath("models", "pix2pix"))
    print("Download complete. The model.pict file in the models directory is ready for use.")



'''

### To export output model from pix2pix-tensorflow to tensorflow.js/ml5.js:
# From https://medium.com/@dongphilyoo/how-to-train-pix2pix-model-and-generating-on-the-web-with-ml5-js-87d879fb4224
    # https://github.com/dongphilyoo/pix2pix-ml5-demo
    # https://github.com/affinelayer/pix2pix-tensorflow

# Run in ml5.js:
pix2pix = ml5.pix2pix('model/2A_models_BtoA.pict', modelLoaded);

'''

