import _thread
import time
import sys
from app import commandline as cmdline
from app import utils
from app.utils import log

import spell.client
from spell.api.models import ValueSpec
client = spell.client.from_environment()


def get_value_spec(values):
    return ValueSpec(values)


def get_username(run=None):
    if run:
        return run.run.creator.user_name
    else:
        return client.api.owner

    
def get_id(run):
    return run.run.id


def wait_until_running(run):
    run.wait_status(client.runs.RUNNING)


def wait_until_complete(run):
    run.wait_status(client.runs.COMPLETE)


def get_run_started_message(run):
    runId = get_id(run)
    msg = "Run {} has started. Visit http://web.spell.run/{}/runs/{} to check progress."
    return msg.format(runId, get_username(run), runId)


def get_kill_run_message(run):
    runId = get_id(run)
    msg = "Enter the command 'spell kill {}' to kill the run if you started it by mistake."
    return msg.format(runId)


def get_runs_page_url():
    return "https://web.spell.run/{}/runs".format(get_username())


def get_hypersearches_page_url():
    return "https://web.spell.run/{}/hyper-searches".format(get_username())


def label_run(run, labelName):
    client.api.add_label_for_run(get_id(run), labelName)


def system_check():
    log("Welcome. Use this application to communicate with the Spell environment.")
    log("Communicating with Spell...")
    log("  Welcome, "+whoami())
    log("System check successful.")

    
def rm(path):
    #cmdline.send("spell rm "+path)
    if not path.startswith("uploads/"):
        raise RuntimeException("rm: You must specify an uploaded resource to delete.")
    client.api.remove_dataset(path[8:])
    

def ls(path):
    listing = cmdline.send("spell ls "+path)
    files = [line.split(" ")[-1] for line in listing.splitlines()]
    files = [f[0:-1] if f.endswith("/") else f for f in files] # Remove trailing slash if one exists
    return files


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
    return client.api.owner # TODO this is not an effective system check because this value is cached locally.


def validate_machine_type(t):
    if t not in ["CPU", "K80"]:
        raise ValueError("Machine type must be CPU or K80")


def hypergrid(params, arg):
    cmd = ["spell", "hyper", "grid"]
    cmd.extend(_flatten(params))
    cmd.append(arg)
    cmdline.send(cmd)

   
def _flatten(params_dict):
    l = []
    for k, v in params_dict.items():
        if not isinstance(v, list):
            v = [v]
        for val in v:
            l.append("--{}".format(k))
            l.append(val)
    return l


def download(path, targetdir=None):
    cmd = "spell cp {}".format(path)
    if targetdir:
        cmd += " {}".format(targetdir)
    cmdline.send(cmd)
    
    



