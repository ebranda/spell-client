
import time
import sys
from app import spell
from app import utils
from app._version import __version__
from app.utils import log

from app import spellstyletransfer as styletransfer
from app import spellpix2pix as pix2pix


########################
# Commands
########################


#### General ####

def command_systemcheck(args):
    spell.system_check()
    

#### Style Transfer ####

def command_st_upload(args):
    styletransfer.upload()

def command_st_transfer(args):
    styletransfer.transfer(args)

def command_st_hyperparams(args):
    styletransfer.hyperparam_search(args)
      
def command_st_download(args):
    styletransfer.download(args)


#### Pix2Pix ####

def command_p2p_imagepairs(args):
    pix2pix.image_pairs(args)

def command_p2p_upload(args):
    pix2pix.upload()

def command_p2p_train(args):
    pix2pix.train(args)

def command_p2p_downloadlatest(args):
    pix2pix.download_latest(args)

def command_p2p_export(args):
    pix2pix.export(args)




########################
# Main
########################

def main():
    if len(sys.argv) < 2:
        log("Usage: python run.py [command] [arguments]")
        sys.exit()
    command_str = sys.argv[1]
    func = globals().get("command_"+command_str)
    if func:
        log("########### Spell Client (version {})".format(__version__))
        args = sys.argv[2:] if len(sys.argv) > 2 else []
        try:
            #spell.cmdline.debug = True
            func(args)
        except Exception as e:
            print(e)
            print("")
            #raise e
        print("###########\n")
    else:
        log("No such command [{}]".format(command_str))
        print("\n")
        sys.exit()

