import random
from collections import defaultdict

def default_dist(dct, default=None):
    if default == None:
        mn = min([v for _, v in dct.iteritems() if v > 0])
        default=mn
    x = defaultdict(lambda *_: default)
    x.update(dct)
    return x

def normalize_dict(dct, mathType=float):
    total = mathType(sum([v for _, v in dct.iteritems()]))
    for k in dct:
        dct[k] = mathType(dct[k]) / total
    return dct

def normalize_tuple_dict(dct, mathType=float, track=0):
    total = defaultdict(mathType)
    for k, v in dct.iteritems():
        total[k[track]] += v
    for k in dct:
        dct[k] = mathType(dct[k]) / total[k[track]]
    return dict(dct) 
        

def rand_generator(dct, normalize=False, mathType=float):
    """
    Returns function (zero arguments) that returns random elements 
    according distribution in input distionary (key = element, 
    value = probability). Expects that probabilities sum to 1.
    """
    L = dct
    if type(dct)==dict or type(dct) == defaultdict:
        L = [[v, k] for (k, v) in dct.iteritems()]
    L = [list(v) for v in L]
    L.sort(reverse=True, key=lambda (x, _): x)
    if normalize:
        total = mathType(sum([x for x, _ in L]))
        L = [(mathType(x) / total, y) for x, y in L]
    #TODO: vyber spravny algoritmus 
    s = mathType(0.0)
    for i in range(len(L)):
        s += L[i][0]
        L[i][0] = s
    def function():
        r = random.random()
        i = 0
        while 0 < len(L) and r > L[i][0]:
            i += 1
        if i >= len(L): 
            i = len(L) - 1
        return L[i][1] 
    return function

def dist_to_json(distribution):
    if type(distribution) in [dict, defaultdict]:
        return distribution
    else:
        raise "Not correct distribution type"
        