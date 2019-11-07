import os 
import shutil

    
def filepath(segment, *segments):
    return os.path.join(segment, *segments)

def name(path):
    return os.path.split(path)[-1]

def isFile(path):
    return os.path.isfile(path)

def mv(sourcePath, targetPath):
    os.rename(sourcePath, targetPath)

def mkdir(path):
    if exists(path):
        return
    os.mkdir(path)
    
def isEmpty(dirpath):
    return len(ls(dirpath)) == 0
    
def ls(dirpath):
    return sorted([f for f in os.listdir(dirpath) if not f.startswith(".")])
    
def exists(path):
    return os.path.exists(path)

def rm(path):
    if not exists(path):
        return
    if path.startswith("../") or path.startswith("/"):
        raise RuntimeError("Stubbornly refusing to delete directories above this one")
    shutil.rmtree(path)

def is_type(filename, extensions):
    for ext in extensions:
        if filename.endswith(ext):
            return True
    return False
    
def find_first(dir_path, file_names):
    if exists(dir_path):
        file_names_lower = [fname.lower() for fname in file_names]
        for fname in ls(dir_path):
            if fname.lower() in file_names_lower:
                return fname
    return None

def cacheSet(key, val):
    d = filepath("app", "cache")
    if not exists(d):
        mkdir(d)
    cacheFile = filepath(d, key)
    f = open(cacheFile, "w")
    f.write(str(val))
    f.close()


def cacheGet(key):
    cacheFile = filepath("app", "cache", key)
    if exists(cacheFile):
        f = open(cacheFile, "r")
        return f.read()
    return None

