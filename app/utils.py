import skimage
import os


def isInteger(var):
    try:
        int(var)
        return True
    except:
        return False


def isNumeric(var):
    try:
        float(var)
        return True
    except:
        return False


def log(msg):
    print("    {}".format(msg))

    
    
