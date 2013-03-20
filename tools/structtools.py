import collections
import functools

def listToStr(a, indent=0):
    if len(a) == 0: return '[]'
    indentStr = ' ' * indent
    if indent > 1:        
        return '[\n' + ''.join([indentStr + '{0},\n'.format(x) 
                              for x in a]) + (' ' * (indent)) + ']'
    return '[' + ','.join(a) + ']'

def getStructure(value, indent=0):
    # zoznamy: list, set
    # dictionaries: dict, defaultdict
    # instances
    # classespyt .__class__.__name__
    indentStr = " " * indent
    newIndent = indent + 2
    if indent < 0: 
        newIndent = indent
    t = type(value)
    if t == list:
        a = set()
        for x in value:
            a.add(getStructure(x, indent + 2))
        a = list(a)
        return '{indent}list{content}'.format(
            indent=indentStr,
            content=listToStr(a, newIndent)
        )
        #return indentStr + "list[\n" + listToStr(a) + '\n' + indentStr + ']'
    elif t == set:
        a = set()
        for x in value:
            a.add(getStructure(x, indent + 2))
        a = list(a)
        return '{indent}set{content}'.format(
            indent=indentStr,
            content=listToStr(a, newIndent)
        )
    elif t == dict:
        a = set()
        b = set()
        for (key, val) in value.iteritems():
            a.add(getStructure(key, indent + 2))
            b.add(getStructure(val, indent + 2))
        a = list(a)
        b = list(b)
        return '{indent}dict{keys}->{values}'.format(
            indent=indentStr,
            keys=listToStr(a, newIndent),
            values=listToStr(a, newIndent)
        )
    elif t == collections.defaultdict:
        a = set()
        b = set()
        for (key, val) in value.iteritems():
            a.add(getStructure(key, indent + 2))
            b.add(getStructure(val, indent + 2))
        a = list(a)
        b = list(b)
        c = [getStructure(value.default_factory(), newIndent)]
        return '{indent}defaultdict(factory: {factory}){keys}->{values}' \
            .format(
            indent=indentStr,
            factory=listToStr(c, newIndent),
            keys=listToStr(a, newIndent),
            values=listToStr(b, newIndent)
        )
    elif str(t).split("'")[1] == 'instance':
        return indentStr + value.__class__.__name__
    else:
        return indentStr + str(type(value)).split("'")[1]
  
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
        st += (newindent2 + "  " + str(i) + ": " + 
               structToStr(v, newrec, newindent) + "," + newline)
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
        (recursiveFold(struct) for (_, struct) in getIterable(structure)),
        None
    )
    
    
def _recursiveArgMax(structure, stop, selector):
    if stop(structure):
        return ([], structure)
    
    iterable = ((index, _recursiveArgMax(struct, stop, selector)) for (index, struct) in getIterable(structure) if recursiveFold(struct) != None)
    x = reduce(functools.partial(max, key=lambda x: x[1][1]), iterable)
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
    return tuple(reversed(l)), x