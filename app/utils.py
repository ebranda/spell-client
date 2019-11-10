

def isinteger(var):
    try:
        int(var)
        return True
    except:
        return False


def isnumeric(var):
    try:
        float(var)
        return True
    except:
        return False


def getboolean(args, i):
    try:
        argval = getarg(args, i)
        return argval in ["1", "True"]
    except ValueError:
        return False


def getint(args, i, default=None, optional=False):
    val = getarg(args, i, optional, isinteger)
    return int(val) if val else default


def getfloat(args, i, default=None, optional=False):
    val = getarg(args, i, optional, isnumeric)
    return float(val) if val else default


def argequals(args, i, val):
    try:
        argval = getarg(args, i)
        return argval == val
    except ValueError:
        return False


def getstr(args, i, optional=False):
    return str(getarg(args, i, optional))


def getarg(args, i, optional=False, typecallback=None):
    arg_exists = len(args) > i
    if not optional and not arg_exists:
        raise ValueError("Missing argument {}".format(i))
    if typecallback:
        if arg_exists and not typecallback(args[i]):
            raise ValueError("Illegal value for argument {}".format(i))
    if arg_exists:
        return args[i]

   
def checkint(args, i, optional=False):
    getint(args, i, None, optional)


def checknumeric(args, i, optional=False):
    getfloat(args, i, None, optional)


def log(msg):
    print(msg)



    
    
