import _thread
import time
import sys
import webbrowser
from app import utils
from app.utils import log, getstr, getint, getfloat, checkint, checknumeric
from app import spell
from app import filesystem as localfs



images_local = localfs.filepath("images")
images_base_local = localfs.filepath(images_local, "style-transfer-images")
images_base_remote = "uploads/style-transfer-images"
paths = {
    "imagesLocal": images_local,
    "imagesBaseLocal": images_base_local,
    "resultsDirLocal": localfs.filepath("images", "style-transfer-results"),
    "imagesBaseRemote": images_base_remote,
    "vggFileRemote": "uploads/models/imagenet-vgg-verydeep-19.mat",
    "vggFileRemoteName": "imagenet-vgg-verydeep-19.mat"
}

if not localfs.exists(paths["imagesLocal"]): 
    localfs.mkdir(paths["imagesLocal"])
if not localfs.exists(paths["imagesBaseLocal"]): 
    localfs.mkdir(paths["imagesBaseLocal"])
#if not localfs.exists(paths["stylesDirLocal"]): 
#    localfs.mkdir(paths["stylesDirLocal"])
#if not localfs.exists(paths["contentDirLocal"]): 
#    localfs.mkdir(paths["contentDirLocal"])
if not localfs.exists(paths["resultsDirLocal"]): 
    localfs.mkdir(paths["resultsDirLocal"])

    
def upload():
    log("Uploading images for style transfer...")
    _validate_local()
    spell.upload(paths["imagesBaseLocal"], paths["imagesBaseRemote"])
    log("Upload complete.")


def transfer(args):
    log("Transferring style. Please wait...")
    img_group_name = getstr(args, 0)
    neural_args = args[1:]
    _validate_neural_args(neural_args)
    imgs_base_dir = localfs.filepath(paths["imagesBaseLocal"], img_group_name)
    style_imgs_dir = localfs.filepath(imgs_base_dir, "styles")
    style_imgs = localfs.ls(style_imgs_dir)
    content_img_dir = localfs.filepath(imgs_base_dir, "content")
    content_img = localfs.ls(content_img_dir)[0]
    neural_style_cmd = _neural_style_cmd(neural_args, style_imgs, content_img)
    run = spell.client.runs.new(
        command = neural_style_cmd,
        machine_type = "K80", 
        github_url = "https://github.com/cysmith/neural-style-tf",
        attached_resources = _mounts(img_group_name)
    )
    spell.wait_until_running(run)
    run_id = spell.get_id(run)
    spell.label_run(run, "Style Transfer single")
    logFilePath = localfs.filepath(paths["resultsDirLocal"], "log-run-{}.txt".format(run_id))
    with open(logFilePath, "w") as f:
        f.write("{} = {}\n".format("Run ID", run_id))
        f.write("{} = {}\n".format("Command", "python "+sys.argv[0]+" sttransfer " + (" ".join(args))))
        f.write("{} = {}\n".format("Image group", img_group_name))
        f.write("{} = {}\n".format("Style images", " ".join(style_imgs)))
        f.write("{} = {}\n".format("Content image", content_img))
    log(spell.get_run_started_message(run))
    log("When run has completed, run the command 'python run.py stdownload {}'".format(run_id))
    log("to download the result file to images/results folder.")
    #if input("Open runs page in browser? [y|n]: ") == "y":
    #    webbrowser.open_new_tab(spell.get_runs_page_url())

      
def hyperparam_search(args):
    log("Building hyperparameter grid. Please wait...")
    img_group_name = getstr(args, 0)
    neural_args = args[1:]
    _validate_neural_args(neural_args)
    if not neural_args:
        neural_args.append("500")
    neural_args.append(":STYLE_WEIGHT:")
    neural_args.append(":TEMPORAL_WEIGHT:")
    imgs_base_dir = localfs.filepath(paths["imagesBaseLocal"], img_group_name)
    style_imgs_dir = localfs.filepath(imgs_base_dir, "styles")
    style_imgs = localfs.ls(style_imgs_dir)
    content_img_dir = localfs.filepath(imgs_base_dir, "content")
    content_img = localfs.ls(content_img_dir)[0]
    neural_style_cmd = _neural_style_cmd(neural_args, style_imgs, content_img)
    search = spell.client.hyper.new_grid_search(
        {
            "STYLE_WEIGHT": spell.get_value_spec(["1e4","1e1","1e7"]), 
            "TEMPORAL_WEIGHT": spell.get_value_spec(["2e2","2e6","2e-2"])
        },
        command = neural_style_cmd, 
        machine_type = "K80", 
        github_url = "https://github.com/cysmith/neural-style-tf",
        attached_resources = _mounts(img_group_name)
    )
    for run in search.runs:
        spell.label_run(run, "Style Transfer hyperparams")
    logFilePath = localfs.filepath(paths["resultsDirLocal"], "log-hyperparams-{}.txt".format(search.id))
    with open(logFilePath, "w") as f:
        f.write("{} = {}\n".format("Search ID", search.id))
        f.write("{} = {}\n".format("Command", "python "+sys.argv[0]+" sthyperparams " + (" ".join(args))))
        f.write("{} = {}\n".format("Image group", img_group_name))
        f.write("{} = {}\n".format("Style images", " ".join(style_imgs)))
        f.write("{} = {}\n".format("Content image", content_img))
    msg = "Hyperparameter search {} has started. Visit https://web.spell.run/{}/hyper-searches/{} for progress."
    msg += "\nWhen all runs have completed, execute 'python run.py stdownload [run-number]'"
    msg += "\nfor each run in the search to download the result files."
    log(msg.format(search.id, spell.get_username(), search.id))
    #if input("Open searches page in browser? [y|n]: ") == "y":
        #webbrowser.open_new_tab(spell.get_hypersearches_page_url())


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


def _mounts(image_group_name):
    resources = {
        paths["vggFileRemote"]: paths["vggFileRemoteName"],
        paths["imagesBaseRemote"]+"/"+image_group_name+"/styles": "styles",
        paths["imagesBaseRemote"]+"/"+image_group_name+"/content": "image_input"
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
    for d in localfs.ls(paths["imagesBaseLocal"]):
        style_images = localfs.ls(localfs.filepath(paths["imagesBaseLocal"], d, "styles"))
        content_images = localfs.ls(localfs.filepath(paths["imagesBaseLocal"], d, "content"))
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



