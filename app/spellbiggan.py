import _thread
import time
import skimage
import os
from app import spell
from app import utils
from app.utils import log
from app import filesystem as localfs


# https://github.com/taki0112/BigGAN-Tensorflow
# ERRORS OUT WITH MEMORY ERROR (posted to Github issues and waiting for reply)


paths = {
    "imagesLocal": localfs.filepath("images"),
    "datasetLocal": localfs.filepath("images", "big-gan-dataset"),
    "datasetName": "images",
    "datasetRemoteDir": "uploads/big-gan-dataset"
}


def upload(args):
    """
    Runs a BigGAN image upload job on Spell.
    
    """
    log("Preparing to upload images...")
    d = localfs.filepath(paths["datasetLocal"], paths["datasetName"])
    if localfs.isempty(d):
        raise RuntimeError("Missing images in dataset folder "+d)
    def validate_filenames(names):
        for n in names:
            if " " in n:
                raise ValueError("Image file names cannot contain spaces. [{}]".format(n)) # TODO add non-alphanumeric character checking
    validate_filenames(localfs.ls(d))
    log("Uploading. Please wait...")
    spell.upload(paths["datasetLocal"], paths["datasetRemoteDir"])
    log("Upload complete.")


def train(args, machine_type="K80"):
    """
    Runs a BigGAN-Tensorflow model training run on Spell. See https://github.com/taki0112/BigGAN-Tensorflow
    
    """
    log("Preparing to train BigGAN model. Please wait...")
    spell.validate_machine_type(machine_type)
    dcgan_cmd = "python main.py --phase train --batch_size 256 --dataset {} --gan_type hinge --img_size 128".format(paths["datasetName"])
    run = spell.client.runs.new(
        command = dcgan_cmd, 
        machine_type = machine_type,
        github_url = "https://github.com/taki0112/BigGAN-Tensorflow.git",
        attached_resources = {
            paths["datasetRemoteDir"]: "dataset"
        }
    )
    spell.label_run(run, "BigGAN training")
    spell.wait_until_running(run)
    run_id = spell.get_id(run)
    localfs.cacheset("BigGANTrainingRunId", run_id)
    log(spell.get_run_started_message(run))


