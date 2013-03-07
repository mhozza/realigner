import collections


def getStructure(value):
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
  
def getIterable(structure):
    t = type(structure)
    if t == list or t == tuple:
        return ((i, structure[i]) for i in range(len(structure))) 
    if t == dict or t == collections.defaultdict:
        return structure.iteritems()
    raise 'Unknown structure!'
        
    
def structToStr(value, rec = -1, indent = ""):
    t = type(value)
    iterable = None
    tp = ""
    if t == type(list()):
        iterable = ((i, value[i]) for i in range(len(value)))
        tp = "list"
    elif t == type(tuple()):
        iterable = ((i, value[i]) for i in range(len(value)))
        tp = "tuple"
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
    
    
def recursiveFold(
    structure,
    function=max,
    stop=lambda x:type(x) not in [list, dict, collections.defaultdict],
):
    
    if stop(structure):
        return structure
    return reduce(
        function, 
        (recursiveFold(struct) for (_, struct) in getIterable(structure))
    )
    
    
def _recursiveArgMax(structure, stop, selector):
    if stop(structure):
        return ([], structure)
    
    iterable = ((index, recursiveFold(struct)) for (index, struct) in getIterable(structure))
    x = reduce(max, iterable, key=lambda x: x[1][1])
    l = x[1][0]
    l.append(x[0])
    return l, x[1][1]    
    
def recursiveArgMax(
    structure,
    selector=max,
    stop=lambda x:type(x) not in [list, dict, collections.defaultdict],
):
    """
    returns tuple (x, y) where x is the tuple of indexes into structure and y is 
    'maximal' value where max relation is provided in selector
    """
    l, x = _recursiveArgMax(structure, stop, selector)
    return tuple(l), x