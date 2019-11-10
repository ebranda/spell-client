import os 
import shutil

    
def filepath(segment, *segments):
    return os.path.join(segment, *segments)

def name(path):
    return os.path.split(path)[-1]

def is_file(path):
    return os.path.isfile(path)

def mv(source_path, target_path):
    os.rename(source_path, target_path)

def mkdir(path):
    if exists(path):
        return
    os.mkdir(path)
    
def isempty(dirpath):
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

def istype(filename, extensions):
    for ext in extensions:
        if filename.endswith(ext):
            return True
    return False
    
def findfirst(dir_path, file_names):
    if exists(dir_path):
        file_names_lower = [fname.lower() for fname in file_names]
        for fname in ls(dir_path):
            if fname.lower() in file_names_lower:
                return fname
    return None

def cacheset(key, val):
    d = filepath("app", "cache")
    if not exists(d):
        mkdir(d)
    cache_file = filepath(d, key)
    f = open(cache_file, "w")
    f.write(str(val))
    f.close()


def cacheget(key):
    cache_file = filepath("app", "cache", key)
    if exists(cache_file):
        f = open(cache_file, "r")
        return f.read()
    return None

