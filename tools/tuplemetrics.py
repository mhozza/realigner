
def tadd(a, b):
    if len(a) != len(b):
        raise "Incompatible types"
    return tuple([a[i] + b[i] for i in range(len(a))])

def tless(a, b):
    if len(a) != len(b):
        raise "Incompatible types"
    for i in range(len(a)):
        if a[i] >= b[i]:
            return False
    return True


def tlesssome(a, b):
    if len(a) != len(b):
        raise "Incompatible types"
    for i in range(len(a)):
        if a[i] < b[i]:
            return True
    return False