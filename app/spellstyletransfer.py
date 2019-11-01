import _thread
import time
import sys
import webbrowser
from app import utils
from app import spell
from app import filesystem as localfs



imagesBaseLocal = localfs.filepath("images", "style-transfer-images")
imagesBaseRemote = "uploads/style-transfer-images"
paths = {
    "imagesBaseLocal": imagesBaseLocal,
    "stylesDirLocal": localfs.filepath(imagesBaseLocal, "styles"),
    "contentDirLocal": localfs.filepath(imagesBaseLocal, "content"),
    "resultsDirLocal": localfs.filepath("images", "results"),
    "imagesBaseRemote": imagesBaseRemote,
    "stylesDirRemote": imagesBaseRemote+"/styles",
    "contentDirRemote": imagesBaseRemote+"/content",
    "vggFileRemote": "uploads/models/imagenet-vgg-verydeep-19.mat",
    "vggFileRemoteName": "imagenet-vgg-verydeep-19.mat"
}


def upload(machineType="CPU"):
    print("Uploading images...")
    # Run validation
    _validateLocal()
    spell.validateMachineType(machineType)
    # Do upload
    spell.upload(paths["imagesBaseLocal"], paths["imagesBaseRemote"])
    print("Upload complete.")


def transfer(neuralArgs, machineType="K80"):
    print ("Preparing to transfer...")
    _validateNeuralArgs(neuralArgs)
    spell.validateMachineType(machineType)
    print("Transferring style. Please wait...")
    styleImg = localfs.ls(paths["stylesDirLocal"])[0]
    contentImg = localfs.ls(paths["contentDirLocal"])[0]
    neuralStyleCmd = _neuralStyleCmd(neuralArgs, styleImg, contentImg)
    run = spell.client.runs.new(
        command = neuralStyleCmd, 
        machine_type = machineType, 
        github_url = "https://github.com/cysmith/neural-style-tf",
        attached_resources = _mounts()
    )
    spell.waitUntilRunning(run)
    runId = spell.getId(run)
    spell.labelRun(run, "Style Transfer single")
    logFileName = localfs.filepath("images", "results", "log-run-{}.txt".format(runId))
    with open(logFileName, "w") as f:
        f.write("{} = {}\n".format("Run ID", runId))
        f.write("{} = {}\n".format("Command", "python "+sys.argv[0]+" transfer "+" ".join(neuralArgs)))
        f.write("{} = {}\n".format("Style image", styleImg))
        f.write("{} = {}\n".format("Content image", contentImg))
    print(spell.getRunStartedMessage(run))
    msg = "When run has completed, run the command 'python run.py download {}'"
    msg += "\nto download the result file to images/results folder."
    print(msg.format(runId))
    #if input("Open runs page in browser? [y|n]: ") == "y":
    #    webbrowser.open_new_tab(spell.getRunsPageURL())

      
def hyperparamSearch(neuralArgs, machineType="K80"):
    print ("Preparing to search hyperparameters...")
    _validateNeuralArgs(neuralArgs)
    spell.validateMachineType(machineType)
    print("Building hyperparameter grid. Please wait...")
    if neuralArgs:
        neuralArgs = neuralArgs[0:1]
    neuralArgs.append(":STYLE_WEIGHT:")
    neuralArgs.append(":TEMPORAL_WEIGHT:")
    styleImg = localfs.ls(paths["stylesDirLocal"])[0]
    contentImg = localfs.ls(paths["contentDirLocal"])[0]
    neuralStyleCmd = _neuralStyleCmd(neuralArgs, styleImg, contentImg)
    search = spell.client.hyper.new_grid_search(
        {
            "STYLE_WEIGHT": spell.getValueSpec(["1e4","1e1","1e7"]), 
            "TEMPORAL_WEIGHT": spell.getValueSpec(["2e2","2e6","2e-2"])
        },
        command = neuralStyleCmd, 
        machine_type = machineType, 
        github_url = "https://github.com/cysmith/neural-style-tf",
        attached_resources = _mounts()
    )
    for run in search.runs:
        spell.labelRun(run, "Style Transfer hypersearch")
    msg = "Search {} has started. Visit https://web.spell.run/{}/hyper-searches for progress."
    msg += "\nWhen all runs have completed, execute 'python run.py download [run-number]'"
    msg += "\nfor each run in the search to download the result files to images/results folder."
    print(msg.format(search.id, spell.getUsername()))
    if input("Open searches page in browser? [y|n]: ") == "y":
        webbrowser.open_new_tab(spell.getHypersearchesPageURL())


def download(args):
    if not args:
        raise RuntimeError("The download command requires a run number")
    for arg in args:
        if not utils.isInteger(arg):
            raise ValueError("Run number must be an integer")
    print ("Fetching remote files...")
    if not localfs.exists(paths["resultsDirLocal"]):
        localfs.mkdir(paths["resultsDirLocal"])
    for runNumber in args:
        spell.download("runs/{}/image_output/result/result.png".format(runNumber))
        targetPath = localfs.filepath(paths["resultsDirLocal"], "result-{}.png".format(runNumber))
        localfs.mv("result.png", targetPath)
        print ("Saved result file [{}]".format(targetPath))


def _mounts():
    resources = {
        paths["vggFileRemote"]: paths["vggFileRemoteName"],
        paths["stylesDirRemote"]: "styles",
        paths["contentDirRemote"]: "image_input"
    }
    return resources


def _neuralStyleCmd(args, styleImg, contentImg):
    cmd = "python neural_style.py --style_imgs {} --content_img {}".format(styleImg, contentImg)
    if len(args) > 0:
        cmd += " --max_size "+args[0]
    if len(args) > 1:
        cmd += " --style_weight "+args[1]
    if len(args) > 2:
        cmd += " --temporal_weight "+args[2]
    return cmd


def _validateLocal():
    if not localfs.exists(paths["imagesBaseLocal"]): 
        localfs.mkdir(paths["imagesBaseLocal"])
    if not localfs.exists(paths["stylesDirLocal"]): 
        localfs.mkdir(paths["stylesDirLocal"])
    if not localfs.exists(paths["contentDirLocal"]): 
        localfs.mkdir(paths["contentDirLocal"])
    styleImages = localfs.ls(paths["stylesDirLocal"])
    contentImages = localfs.ls(paths["contentDirLocal"])
    if not styleImages:
        raise FileNotFoundError("Style images folder [{}] is empty.".format(paths["stylesDirLocal"]))
    if not contentImages:
        raise FileNotFoundError("Content images folder [{}] is empty.".format(paths["contentDirLocal"]))
    def validateFilenames(names):
        for n in names:
            if " " in n:
                raise ValueError("Image file names cannot contain spaces.") # TODO add non-alphanumeric character checking
    validateFilenames(styleImages)
    validateFilenames(contentImages)


def _validateNeuralArgs(args):
    if len(args) > 0 and not utils.isInteger(args[0]):
        raise ValueError("max_size parameter must be an integer")
    if len(args) > 1 and not utils.isNumeric(args[1]):
        raise ValueError("style_weight parameter must be a number")
    if len(args) > 2 and not utils.isNumeric(args[2]):
        raise ValueError("temporal_weight parameter must be a number")
