from collections import defaultdict


def position_independent_indels(posterior_table, mathType):
    indelsX = defaultdict(mathType)
    indelsY = defaultdict(mathType)
    for x in range(len(posterior_table)):
        for y, dct in posterior_table[x].iteritems():
            dl = []
            for (state, _sdx, _sdy), prob in dct.iteritems():
                if (_sdx, _sdy) not in [(0, 1), (1, 0)]:
                    continue
                if _sdx == 0:
                    indelsY[(state, y)] += prob
                else:
                    indelsX[(state, x)] += prob
                dl.append((state, _sdx, _sdy))
            for x in dl:
                del dct[x]
    for x in range(len(posterior_table)):
        for y, dct in posterior_table[x].iteritems():
            def missing(self, key, x=x, y=y):
                if not isinstance(key, tuple):
                    return mathType()
                if len(key) != 3:
                    return mathType()
                (state, _sdx, _sdy) = key
                if (_sdx, _sdy) not in [(0, 1), (1, 0)]:
                    return mathType()
                if _sdx == 0:
                    return indelsY[y]
                else:
                    return indelsX[x]
            dct.__missing__ = missing
