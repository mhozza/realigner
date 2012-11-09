import itertools
import math

def every(N = None):
    if N == None:
        return itertools.repeat(True)
    return itertools.repeat(True, N)

def last(N, k=1):
    return itertools.chain(itertools.repeat(False, N - k), itertools.repeat(True, k))

def first(N, k=1):
    return itertools.chain(itertools.repeat(True, k), itertools.repeat(False, N - k))

def sqrt(N):
    sqrtN = int(math.sqrt(N))
    sqrtN = sqrtN if sqrtN > 0 else 1
    count = N / sqrtN
    rest = N % sqrtN
    if rest == 0:
        count -= 1
        rest = sqrtN
    return itertools.chain(
        itertools.chain(*itertools.tee(first(sqrtN), count)),
        first(rest))    