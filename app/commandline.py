import subprocess
from app.utils import log

debug = False

def send(args, verbose=False):
    if not args: return None
    if verbose or debug: 
        log("SENDING CMD: "+str(args))
    if not debug:
        if isinstance(args, str):
            args = args.split(" ")
        output = subprocess.check_output(args).decode("utf-8")
        return output
    return []



