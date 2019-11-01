import _thread
import time
import sys
from app import commandline as cmdline
from app import utils

import spell.client
from spell.api.models import ValueSpec
client = spell.client.from_environment()


def getValueSpec(values):
    return ValueSpec(values)


def getUsername(run=None):
    if run:
        return run.run.creator.user_name
    else:
        return client.api.owner

    
def getId(run):
    return run.run.id


def waitUntilRunning(run):
    run.wait_status(client.runs.RUNNING)


def waitUntilComplete(run):
    run.wait_status(client.runs.COMPLETE)


def getRunStartedMessage(run):
    runId = getId(run)
    msg = "Run {} has started. Visit http://web.spell.run/{}/runs/{} to check progress."
    return msg.format(runId, getUsername(run), runId)


def getRunsPageURL():
    return "https://web.spell.run/{}/runs".format(getUsername())


def getHypersearchesPageURL():
    return "https://web.spell.run/{}/hyper-searches".format(getUsername())


def labelRun(run, labelName):
    client.api.add_label_for_run(getId(run), labelName)


def systemcheck(args):
    print("Welcome. Use this application to communicate with the Spell environment.")
    print("Communicating with Spell...")
    print(whoami())
    print("Done system check.")

    
def rm(path):
    #cmdline.send("spell rm "+path)
    if not path.startswith("uploads/"):
        raise RuntimeException("rm: You must specify an uploaded resource to delete.")
    client.api.remove_dataset(path[8:])
    

def ls(path):
    listing = cmdline.send("spell ls "+path)
    return [line.split(" ")[-1] for line in listing.splitlines()]


def exists(path):
    if not path: return False
    segments = path.split("/")
    f = segments[-1]
    parent = "/".join(segments[0:-1])
    listing = ls(parent)
    return f in listing


def upload(localpath, remotepath):
    if exists(remotepath):
        rm(remotepath)
    cmdline.send("spell upload "+localpath)


def whoami():
    return client.api.owner


def validateMachineType(t):
    if t not in ["CPU", "K80"]:
        raise ValueError("Machine type must be CPU or K80")


def hypergrid(params, arg):
    cmd = ["spell", "hyper", "grid"]
    cmd.extend(_flatten(params))
    cmd.append(arg)
    cmdline.send(cmd)

   
def _flatten(paramsDict):
    l = []
    for k, v in paramsDict.items():
        if not isinstance(v, list):
            v = [v]
        for val in v:
            l.append("--{}".format(k))
            l.append(val)
    return l


def download(path, targetDir=None):
    cmd = "spell cp {}".format(path)
    if targetDir:
        cmd += " {}".format(targetDir)
    cmdline.send(cmd)
    
    





'''

def run_OBS(params, arg):
    cmd = ["spell", "run"]
    cmd.extend(_flatten(params))
    cmd.append(arg)
    cmdline.send(cmd)

def _getActiveRunId_OBS():
    runMeta = [line for line in cmdline.send("spell ls runs").splitlines()]
    activeRunIds = [line.split(" ")[-2] for line in runMeta if "active" in line]
    if not activeRunIds: return None
    return activeRunIds[-1]

def waitForActiveRunId_OBS():
    runId = _getActiveRunId()
    attempts = 0
    while not runId and attempts < 10:
        attempts += 1
        time.sleep(2)
        runId = _getActiveRunId()
    return runId
'''


