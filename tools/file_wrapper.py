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
            if len(mode) > 0:
                if mode[0] == 'r':
                    return gzip.open(filename, 'rb')
                elif mode[0] == 'w':
                    return gzip.open(filename, 'wb')
                return None
            return None
    if mode == None:
        return open(filename)
    return open(filename, mode)      
