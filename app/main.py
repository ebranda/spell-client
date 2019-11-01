
import time
import sys
from app import spell
from app import spellstyletransfer as styletransfer
from app import spellpix2pix as pix2pix
from app import utils
from app._version import __version__
    


########################
# Commands
########################


#### General ####

def command_systemcheck(args):
    spell.systemcheck()
    

#### Style Transfer ####

def command_upload(args):
    styletransfer.upload()

def command_transfer(args):
    styletransfer.transfer(args)

def command_hyperparams(args):
    styletransfer.hyperparamSearch(args)
      
def command_download(args):
    styletransfer.download(args)


#### Pix2Pix ####

def command_pix2pixupload(args):
    pix2pix.upload()
    
def command_pix2pixdatasetrunid(args):
    pix2pix.setDatasetRunId(args)

def command_pix2pixtrain(args):
    pix2pix.train(args)

def command_pix2pixexport(args):
    pix2pix.export(args)



########################
# Main
########################

def main():
    if len(sys.argv) < 2:
        print("Usage: python run.py [command] [arguments]")
        sys.exit()
    commandStr = sys.argv[1]
    func = globals().get("command_"+commandStr)
    if func:
        print ("\n########### Spell Client (version {}) ###########".format(__version__))
        args = sys.argv[2:] if len(sys.argv) > 2 else []
        try:
            #spell.cmdline.debug = True
            func(args)
        except Exception as e:
            print(e)
        print("\n")
    else:
        print("No such command [{}]".format(commandStr))
        print("\n")
        sys.exit()

