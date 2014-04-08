__author__ = 'michal'

def merge(which, *args):
    iters = [iter(arg) for arg in args]
    def get_next(w):
        return next(iters[w])
    return (get_next(w) for w in which)

def avg(l):
    return sum(l)/float(len(l))

def dict_avg(ld):
    if ld is None:
        return None
    d = None
    for i in ld:
        if d == None:
            d = i
        else:
            if i is not None:
                for k, v in i.iteritems():
                    if type(v) is float:
                        d[k] += v
                    else:
                        d[k] = dict_avg(v)
    if d is not None:
        for k, v in d.iteritems():
            if type(v) is float:
                d[k] = v/float(len(ld))
    return d

