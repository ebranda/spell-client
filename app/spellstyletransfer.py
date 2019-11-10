import _thread
import time
import sys
import webbrowser
from app import utils
from app.utils import log, getint, getfloat, checkint, checknumeric
from app import spell
from app import filesystem as localfs



images_local = localfs.filepath("images")
images_base_local = localfs.filepath(images_local, "style-transfer-images")
images_base_remote = "uploads/style-transfer-images"
paths = {
    "imagesLocal": images_local,
    "imagesBaseLocal": images_base_local,
    "stylesDirLocal": localfs.filepath(images_base_local, "styles"),
    "contentDirLocal": localfs.filepath(images_base_local, "content"),
    "resultsDirLocal": localfs.filepath("images", "style-transfer-results"),
    "imagesBaseRemote": images_base_remote,
    "stylesDirRemote": images_base_remote+"/styles",
    "contentDirRemote": images_base_remote+"/content",
    "vggFileRemote": "uploads/models/imagenet-vgg-verydeep-19.mat",
    "vggFileRemoteName": "imagenet-vgg-verydeep-19.mat"
}

if not localfs.exists(paths["imagesLocal"]): 
    localfs.mkdir(paths["imagesLocal"])
if not localfs.exists(paths["imagesBaseLocal"]): 
    localfs.mkdir(paths["imagesBaseLocal"])
if not localfs.exists(paths["stylesDirLocal"]): 
    localfs.mkdir(paths["stylesDirLocal"])
if not localfs.exists(paths["contentDirLocal"]): 
    localfs.mkdir(paths["contentDirLocal"])
if not localfs.exists(paths["resultsDirLocal"]): 
    localfs.mkdir(paths["resultsDirLocal"])

        
def upload(machine_type="CPU"):
    log("Uploading images for style transfer...")
    # Run validation
    _validate_local()
    spell.validate_machine_type(machine_type)
    # Do upload
    spell.upload(paths["imagesBaseLocal"], paths["imagesBaseRemote"])
    log("Upload complete.")


def transfer(neural_args, machine_type="K80"):
    log ("Preparing to transfer...")
    spell.validate_machine_type(machine_type)
    log("Transferring style. Please wait...")
    style_imgs = localfs.ls(paths["stylesDirLocal"])
    content_img = localfs.ls(paths["contentDirLocal"])[0]
    _validate_neural_args(neural_args)
    neural_style_cmd = _neural_style_cmd(neural_args, style_imgs, content_img)
    run = spell.client.runs.new(
        command = neural_style_cmd,
        machine_type = machine_type, 
        github_url = "https://github.com/cysmith/neural-style-tf",
        attached_resources = _mounts()
    )
    spell.wait_until_running(run)
    run_id = spell.get_id(run)
    spell.label_run(run, "Style Transfer single")
    logFilePath = localfs.filepath(paths["resultsDirLocal"], "log-run-{}.txt".format(run_id))
    with open(logFilePath, "w") as f:
        f.write("{} = {}\n".format("Run ID", run_id))
        f.write("{} = {}\n".format("Command", "python "+sys.argv[0]+" transfer " + (" ".join(neural_args))))
        f.write("{} = {}\n".format("Style images", " ".join(style_imgs)))
        f.write("{} = {}\n".format("Content image", content_img))
    log(spell.get_run_started_message(run))
    log("When run has completed, run the command 'python run.py stdownload {}'".format(run_id))
    log("to download the result file to images/results folder.")
    #if input("Open runs page in browser? [y|n]: ") == "y":
    #    webbrowser.open_new_tab(spell.get_runs_page_url())

      
def hyperparam_search(args, machine_type="K80"):
    log ("Preparing to search hyperparameters...")
    spell.validate_machine_type(machine_type)
    log("Building hyperparameter grid. Please wait...")
    neural_args = args[0:1] if args else []
    _validate_neural_args(neural_args)
    neural_args.append(":STYLE_WEIGHT:")
    neural_args.append(":TEMPORAL_WEIGHT:")
    style_imgs = localfs.ls(paths["stylesDirLocal"])
    content_img = localfs.ls(paths["contentDirLocal"])[0]
    neural_style_cmd = _neural_style_cmd(neural_args, style_imgs, content_img)
    search = spell.client.hyper.new_grid_search(
        {
            "STYLE_WEIGHT": spell.get_value_spec(["1e4","1e1","1e7"]), 
            "TEMPORAL_WEIGHT": spell.get_value_spec(["2e2","2e6","2e-2"])
        },
        command = neural_style_cmd, 
        machine_type = machine_type, 
        github_url = "https://github.com/cysmith/neural-style-tf",
        attached_resources = _mounts()
    )
    for run in search.runs:
        spell.label_run(run, "Style Transfer hypersearch")
    msg = "Search {} has started. Visit https://web.spell.run/{}/hyper-searches for progress."
    msg += "\nWhen all runs have completed, execute 'python run.py stdownload [run-number]'"
    msg += "\nfor each run in the search to download the result files."
    log(msg.format(search.id, spell.get_username()))
    if input("Open searches page in browser? [y|n]: ") == "y":
        webbrowser.open_new_tab(spell.get_hypersearches_page_url())


def download(args):
    if not args:
        raise RuntimeError("The download command requires a run number")
    for arg in args:
        if not utils.isinteger(arg):
            raise ValueError("Run number must be an integer")
    log ("Fetching remote files...")
    if not localfs.exists(paths["resultsDirLocal"]):
        localfs.mkdir(paths["resultsDirLocal"])
    for run_number in args:
        spell.download("runs/{}/image_output/result/result.png".format(run_number))
        target_path = localfs.filepath(paths["resultsDirLocal"], "result-{}.png".format(run_number))
        localfs.mv("result.png", target_path)
        log ("Saved result file [{}]".format(target_path))


def _mounts():
    resources = {
        paths["vggFileRemote"]: paths["vggFileRemoteName"],
        paths["stylesDirRemote"]: "styles",
        paths["contentDirRemote"]: "image_input"
    }
    return resources


def _neural_style_cmd(args, style_imgs, content_img):
    cmd = "python neural_style.py --style_imgs {} --content_img {}"
    cmd = cmd.format(" ".join(style_imgs), content_img)
    if len(style_imgs) > 1:
        weights = [str(round(1.0 / len(style_imgs), 2)) for img in style_imgs]
        cmd += " --style_imgs_weights " + " ".join(weights)
    if len(args) > 0:
        cmd += " --max_size " + str(getint(args, 0, 512))
    if len(args) > 1:
        cmd += " --style_weight "+args[1]
    if len(args) > 2:
        cmd += " --temporal_weight "+args[2]
    return cmd


def _validate_local():
    style_images = localfs.ls(paths["stylesDirLocal"])
    content_images = localfs.ls(paths["contentDirLocal"])
    if not style_images:
        raise FileNotFoundError("Style images folder [{}] is empty.".format(paths["stylesDirLocal"]))
    if not content_images:
        raise FileNotFoundError("Content images folder [{}] is empty.".format(paths["contentDirLocal"]))
    def validate_filenames(names):
        for n in names:
            if " " in n:
                raise ValueError("Image file names cannot contain spaces.") # TODO add non-alphanumeric character checking
    validate_filenames(style_images)
    validate_filenames(content_images)


def _validate_neural_args(args):
    checkint(args, 0, True)
    checknumeric(args, 1, True)
    checknumeric(args, 2, True)



