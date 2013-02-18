def identity(x):
    return x

def histogram(L, fun=identity):
    D = {}
    for x in L:
        x = fun(x)
        if x not in D:
            D[x] = 1
        else:
            D[x] += 1
    return D