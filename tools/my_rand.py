import random
from collections import defaultdict

def rand_generator(dct):
    """
    Returns function (zero arguments) that returns random elements 
    according distribution in input distionary (key = element, 
    value = probability). Expects that probabilities sum to 1.
    """
    L = dct
    if type(dct)==dict or type(dct) == defaultdict:
        L = [[v, k] for (k, v) in dct.iteritems()]
    L = [list(v) for v in L]
    L.sort(reverse=True)
    #TODO: vyber spravny algoritmus 
    s = 0.0
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