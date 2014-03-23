__author__ = 'michal'

def merge(first, second, which):
    first_iter = iter(first)
    second_iter = iter(second)
    def get_next(w):
        if w == 0:
            return next(first_iter)
        else:
            return next(second_iter)
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

