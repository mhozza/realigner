import collections


def getStructure(value): #TODO: fix this
    t = type(value)
    if t == type(list()):
        a = set()
        for x in value:
            a.add(getStructure(x))
        a = list(a)
        return "list(" + str(a) + ")"
    elif t == type(dict()) or t == type(collections.defaultdict()):
        a = set()
        for (key, val) in value.iteritems():
            a.add((getStructure(key),getStructure(val)))
        a = list(a)
        return "dict(" + str(a) + ")"
    else:
        return str(type(value))
    
    
def structToStr(value, rec = -1, indent = ""):
    t = type(value)
    iterable = None
    tp = ""
    if t == type(list()):
        iterable = ((i, value[i]) for i in range(len(value)))
        tp = "list"
    elif t == type(dict()) or t == type(collections.defaultdict()):
        iterable = value.iteritems()
        tp = "dict"
    if iterable == None:
        return str(value)
    
    newrec = rec - 1
    newindent = indent + "  "
    newindent2 = newindent
    newline = "\n"
    if rec == 0:
        newrec = 0
        newindent = indent
        newline = ""
        newindent2 = ""
    st = tp + "(" + newline
    for (i, v) in iterable:
        st += newindent2 + "  " + str(i) + ": " + structToStr(v, newrec, newindent) + "," + newline
    st += newindent2 + ")"
    return st
    
    
    
    
    
    