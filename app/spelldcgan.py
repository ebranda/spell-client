import _thread
import time
import skimage
import os
from app import spell
from app import utils
from app.utils import log
from app import filesystem as localfs


paths = {
    "imagesLocal": localfs.filepath("images"),
    "datasetLocal": localfs.filepath("images", "dcgan-dataset"),
    "datasetRemoteDir": "uploads/dcgan-dataset"
}


def upload(args):
    """
    Runs a DCGAN image upload job on Spell.
    
    """
    log("Preparing to upload images...")
    if localfs.isempty(paths["datasetLocal"]):
        raise RuntimeError("Missing images in dataset folder "+paths["datasetLocal"])
    def validate_filenames(names):
        for n in names:
            if " " in n:
                raise ValueError("Image file names cannot contain spaces. [{}]".format(n)) # TODO add non-alphanumeric character checking
    validate_filenames(localfs.ls(paths["datasetLocal"]))
    log("Uploading. Please wait...")
    spell.upload(paths["datasetLocal"], paths["datasetRemoteDir"])
    log("Upload complete.")


def train(args, machine_type="K80"):
    """
    Runs a DCGAN-tensorflow model training job on Spell. 
    See https://github.com/carpedm20/DCGAN-tensorflow which has been
    forked to https://github.com/ebranda/DCGAN-tensorflow.git
    
    """
    log("Preparing to train DCGAN model. Please wait...")
    if len(args):
        if utils.isinteger(args[0]):
            epochs = int(args[0])
        else:
            raise ValueError("epochs parameter must be an integer")
    else:
        epochs = 500
    spell.validate_machine_type(machine_type)
    size = 256
    ckpts_to_keep = 3
    sample_freq = 25
    ckpt_freq = 25
    dcgan_cmd = "python main.py --out_name output-{} \
                    --dataset images_{} --input_height={} --output_height={} \
                    --epoch {} --max_to_keep {} --sample_freq {} --ckpt_freq {} \
                    --train --crop"
    dcganCmd = dcganCmd.format(size, size, size, size, epochs, ckpts_to_keep, sample_freq, ckpt_freq)
    run = spell.client.runs.new(
        command = dcgan_cmd, 
        machine_type = machine_type,
        github_url = "https://github.com/ebranda/DCGAN-tensorflow.git",
        pip_packages = ["tqdm", "pillow==5.0.0", "scipy==1.0.1"],
        attached_resources = {
            paths["datasetRemoteDir"]: "data"
        }
    )
    spell.label_run(run, "DCGAN training")
    spell.wait_until_running(run)
    run_id = spell.get_id(run)
    localfs.cacheset("DCGANTrainingRunId", run_id)
    log(spell.get_run_started_message(run))



