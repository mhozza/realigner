import gzip
import sys

def Open(filename, mode=None):
    if filename == '-':
        if mode == None:
            return sys.stdin
        if len(mode) > 0:
            if mode[0] == 'r':
                return sys.stdout
            elif mode[0] == 'w':
                return sys.stderr
            return None
    else:
        ext = filename.split('.')[-1]
        if ext == 'gz':
            if mode == None:
                return gzip.open(filename)
            return gzip.open(filename, mode)
    if mode == None:
        return open(filename)
    return open(filename, mode)      