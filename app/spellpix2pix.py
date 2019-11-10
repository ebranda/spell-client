import _thread
import time
import math
from app import spell
from app import utils
from app import imageutils
from app.utils import log
from app.utils import getint, getboolean, argequals
from app import filesystem as localfs



# Expects image pairs in dataset directory
paths = {
    "imageslocal": localfs.filepath("images"),
    "sourceslocal": localfs.filepath("images", "pix2pix-sources"),
    "datasetlocal": localfs.filepath("images", "pix2pix-dataset"),
    "datasetremote": "uploads/pix2pix-dataset"
}

if not localfs.exists(paths["imageslocal"]): 
    localfs.mkdir(paths["imageslocal"])
    
if not localfs.exists(paths["datasetlocal"]): 
    localfs.mkdir(paths["datasetlocal"])


def image_pairs(args):
    """Builds pairs of images on local computer.
    
    Expects two input images, png or jpg, named A and B in the
    directory images/pix2pix-sources. Exports image pair files to 
    images/pix2pix-dataset.
    
    Args:
        args: The arguments 
            subimage width
            subimage height
            number of subimages in x
            number of subimages in y
            rotate 180 (default False)
            flip horizontal (default False)
            flip vertical (default False)
    
    Raises:
        RuntimeError: If arguments are missing
    """
    log("Preparing to make image pairs...")
    source_dir = paths["sourceslocal"]
    source_a = localfs.findfirst(source_dir, ["A.jpg", "A.jpeg", "A.png"])
    source_b = localfs.findfirst(source_dir, ["B.jpg", "B.jpeg", "B.png"])
    img_path_a = localfs.filepath(source_dir, source_a)
    img_path_b = localfs.filepath(source_dir, source_b)
    log("  Image A: {}".format(img_path_a))
    log("  Image B: {}".format(img_path_b))
    sub_w = getint(args, 0, 0)
    sub_h = getint(args, 1, 0)
    num_x = getint(args, 2, 0)
    num_y = getint(args, 3, 0)
    rotate = getboolean(args, 4)
    flip_h = getboolean(args, 5)
    output_dir_a = localfs.filepath(paths["datasetlocal"], "A")
    output_dir_b = localfs.filepath(paths["datasetlocal"], "B")
    log("Extracting subimages...")
    localfs.rm(paths["datasetlocal"])
    localfs.mkdir(paths["datasetlocal"])
    def process(img_path, out_dir):
        imageutils.extract_subimages(img_path, out_dir, sub_w, sub_h, num_x, num_y, False, 0)
        if rotate:
            imageutils.extract_subimages(img_path, out_dir, sub_w, sub_h, num_x, num_y, True, 180)
            if flip_h:
                imageutils.extract_subimages(img_path, out_dir, sub_w, sub_h, num_x, num_y, True, 180, True)
        elif flip_h:
            imageutils.extract_subimages(img_path, out_dir, sub_w, sub_h, num_x, num_y, True, 0, True)
        
    process(img_path_a, output_dir_a)
    process(img_path_b, output_dir_b)
    log("Building image pairs...")
    pairs_dir_path = localfs.filepath(paths["datasetlocal"], "pairs")
    if not localfs.exists(pairs_dir_path):
        localfs.mkdir(pairs_dir_path)
    for a, b in zip(localfs.ls(output_dir_a), localfs.ls(output_dir_b)):
        img_a_path = localfs.filepath(output_dir_a, a)
        img_b_path = localfs.filepath(output_dir_b, b)
        imageutils.create_pair(pairs_dir_path, img_a_path, img_b_path, a, b)
    localfs.rm(output_dir_a)
    localfs.rm(output_dir_b)
    for fname in localfs.ls(pairs_dir_path):
        fpath = localfs.filepath(pairs_dir_path, fname)
        fpath_new = localfs.filepath(paths["datasetlocal"], fname)
        localfs.mv(fpath, fpath_new)
    localfs.rm(pairs_dir_path)
    log("Done. Image pairs are in the directory '{}'".format(paths["datasetlocal"]))
    log("You can now send the upload command to send the images to Spell.")
    

def upload():
    """Runs a pix2pix image upload and processing job on Spell.
    
    Expects image pair files in images/pix2pix-dataset. These can
    be built using the image_pairs function.
    
    After upload, images are processed to remove alpha channel
    since pix2pix fails on images with alpha channels.
    
    Args:
        machine_type: The machine type to use for the run. Defaults to 'CPU'.
    
    Raises:
        RuntimeError: If image files are missing.
        ValueError: If any image file name is illegal.
    """
    log("Preparing to upload images...")
    if localfs.isempty(paths["datasetlocal"]):
        raise RuntimeError("Missing images in {}".format(paths["datasetlocal"]))
    for filename in localfs.ls(paths["datasetlocal"]):
        if " " in filename:
            # TODO check for non-alphanumeric characters
            raise ValueError("Image file names cannot contain spaces.") 
    log("Removing alpha channel from images...")
    imageutils.strip_alpha_channel(paths["datasetlocal"])
    log("Uploading. Please wait...")
    spell.upload(paths["datasetlocal"], paths["datasetremote"])
    log("Upload complete.")
        

def train(pix2pix_args, machine_type="K80"):
    """Runs a pix2pix model training job on Spell.
    
    Based on https://learn.spell.run/pix2pix.
    
    Args:
        pix2pix_args: The command arguments. Arguments are 
            `max_epochs`, `display_freq`, `resume`, `run_number`
        machine_type: The machine type to use for the run. Defaults to 'K80'.
    
    Raises:
        ValueError: If max_epochs argument is not an integer.
        ValueError: If run id argument is not an integer.
        RuntimeError: If resume argument is provided but run id argument is missing.
    """
    log ("Preparing to train pix2pix model. Please wait...")
    max_epochs = getint(pix2pix_args, 0, 200)
    display_freq = getint(pix2pix_args, 1, 100)
    resume = argequals(pix2pix_args, 2, "resume")
    if resume:
        run_id = _fetch_run_id(pix2pix_args, 3, "pix2pixTrainingRunId")
        checkpoint_dir = "runs/{}/output".format(run_id)
    spell.validate_machine_type(machine_type)
    # Build the spell run command (from the example found at
    # https://learn.spell.run/pix2pix but using remote git repo)
    pix2pix_cmd = "python pix2pix.py \
                    --mode train \
                    --which_direction BtoA \
                    --max_epochs {} \
                    --input_dir dataset \
                    --output_dir output \
                    --display_freq {}"
    pix2pix_cmd = pix2pix_cmd.format(max_epochs, display_freq)
    mounts = {
        paths["datasetremote"]: "dataset"
    }
    # Check for resume flag and modify command if needed
    if resume:
        pix2pix_cmd += " --checkpoint ckpt"
        mounts[checkpoint_dir] = "ckpt"
        log("Resuming training session from run {}".format(run_id))
    # Run the command
    run = spell.client.runs.new(
        command = pix2pix_cmd, 
        machine_type = machine_type, 
        github_url = "https://github.com/affinelayer/pix2pix-tensorflow.git",
        attached_resources = mounts
    )
    spell.label_run(run, "Pix2Pix training")
    spell.wait_until_running(run)
    run_id = spell.get_id(run)
    localfs.cacheset("pix2pixTrainingRunId", run_id)
    log(spell.get_run_started_message(run))
    log(spell.get_kill_run_message(run))


def download_latest(args):
    """Downloads the most recent output image from a training run.
    
    Args:
        args: The command arguments. Accepts a single run id argument.
            If no argument is provided then we try to retrieve the id
            from the cache file created during the last training run.
    
    Raises:
        ValueError: If run id argument is not an integer.
        RuntimeError: If no run id argument is provided or found in cache.
    """
    run_id = _fetch_run_id(args, 0, "pix2pixTrainingRunId")
    log("Downloading latest training output image from run {}...".format(run_id))
    remote_dir = "runs/{}/output/images".format(run_id)
    if not spell.exists(remote_dir):
        log("No server output directory available yet.")
        return
    def get_output_file():
        listing = spell.ls(remote_dir)
        listing.sort()
        return listing[-2]
    f = get_output_file()
    attempts = 0
    while "output" not in f and attempts < 10:
        f = get_output_file()
        attempts += 1
    if "output" not in f:
        raise RuntimeError("Unable to find an output file on server.")
    local_dir = localfs.filepath(paths["imageslocal"], "pix2pix-results")
    spell.download(remote_dir+"/"+f, local_dir)
    log("Latest output file downloaded to '{}'.".format(localfs.filepath(local_dir, f)))


def export(args, machine_type="CPU"):
    """Runs a pix2pix model export job on Spell. Automatically downloads
    the finished model to the local "models" directory.
    
    Args:
        args: The command arguments. Should contain only
            the run id from the training run. If no run id
            is provided then the last run id is retrieved
            from the local cache.
        machine_type: The machine type to use. Defaults to "CPU".
    
    Raises:
        ValueError: If run id argument is not an integer.
        RuntimeError: If no run id argument is provided or found in cache.
    """
    run_id = _fetch_run_id(args, 0, "pix2pixTrainingRunId")
    spell.validate_machine_type(machine_type)
    # Build and run the commands. Bundle the two required
    # commands into one Spell run to simplify management.
    pix2pix_export_cmd = "python pix2pix.py \
                        --mode export \
                        --output_dir output/ \
                        --checkpoint input_model/ \
                        --which_direction BtoA"
    pix2pix_convert_cmd = "python server/tools/export-checkpoint.py \
                        --checkpoint output \
                        --output_file output/model.pict"
    log ("Converting model. Please wait...")
    run = spell.client.runs.new(
        command = pix2pix_export_cmd+";"+pix2pix_convert_cmd, 
        machine_type = machine_type, 
        github_url = "https://github.com/affinelayer/pix2pix-tensorflow.git",
        attached_resources = {
            "runs/{}/output".format(run_id): "input_model"
        }
    )
    spell.label_run(run, "Pix2Pix export")
    spell.wait_until_complete(run)
    # Download the model file now that the run is complete.
    log("Export complete. Downloading model pict file...")
    run.cp("output/model.pict", localfs.filepath("models", "pix2pix"))
    msg = "Download complete. The model.pict file in the models directory "
    msg += "{} is ready for use in tensorflowjs."
    log(msg.format(localfs.filepath("models", "pix2pix")))


def _fetch_run_id(args, i, cachekey):
    """Helper function to fetch a run id.
    
    If a legal run id is not in the arg list then try to get it from the local cache.
    
    Args:
        args: The command arguments list.
        i: The index number of the run id in the args list.
        cachekey: The string name of the cache key containing previous run id.
    
    Raises:
        ValueError: If run id is in args list but is not an integer.
        RuntimeError: If no run id could be found in args list or cache.
    """
    run_id = getint(args, i, None, optional=True)
    if run_id:
        localfs.cacheset(cachekey, run_id)
    else:
        run_id = localfs.cacheget(cachekey)
    if not run_id:
        raise RuntimeError("Unable to find run ID in args or local cache.")
    return run_id



