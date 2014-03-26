import os
from collections import defaultdict
from scipy.stats import norm, gaussian_kde
from classifier_alignment.ClassifierState import ClassifierState, ClassifierIndelState
from classifier_alignment.DataLoader import DataLoader
from tools.utils import merge

precision = 10
pseudocount = 0.001


class ClassifierAnnotationState(ClassifierState):
    def __init__(self, *args, **kwargs):
        ClassifierState.__init__(self, *args, **kwargs)

    def _emission(self, c, seq_x, x, seq_y, y):
        return self.emissions[(seq_x[x], seq_y[y], round((precision - 1) * c))]

    def _classification(self, seq_x, ann_x, seq_y, ann_y):
        def state(i):
            if seq_x[i] != '-' and seq_y[i] != '-':
                return 0
            return 1

        if len(seq_x) != len(seq_y):
            return
        l = len(seq_x)

        ret_match = self.clf.multi_prepare_predict(
            (seq_x, pos, ann_x, seq_y, pos, ann_y)
            for pos in filter(lambda x: state(x) == 0, xrange(l))
        )

        ret_insert = (
            0 for _ in filter(lambda x: state(x) != 0, xrange(l))
        )

        ret = merge(ret_match, ret_insert, (state(x) for x in xrange(l)))
        return ret

    def compute_emissions(self, labels, seq_x, seq_y, ann_x, ann_y):
        classification = self._classification(seq_x, ann_x, seq_y, ann_y)
        data = defaultdict(list)
        count = 0.0
        for label, x, y, c in zip(labels, seq_x, seq_y, classification):
            if label == 'M':
                count += 1
                data[(x, y)].append(c)
        res = dict()

        # todo: move gaussian one level up
        for x in 'ACGT':
            for y in 'ACGT':
                p = len(data[(x, y)]) / count
                if len(data[(x, y)]) > 1:
                    g = gaussian_kde(data[(x, y)])
                    for c in xrange(precision):
                        res[(x, y, c)] = p * g.integrate_box(float(c) / precision, float(c + 1.0) / precision)
                else:
                    for c in xrange(precision):
                        res[(x, y, c)] = p / precision

        return res


class ClassifierAnnotationIndelState(ClassifierIndelState):
    def __init__(self, *args, **kwargs):
        ClassifierIndelState.__init__(self, *args, **kwargs)

    def _classification(self, seq_x, ann_x, seq_y, ann_y):
        def state(i):
            if seq_x[i] != '-' and seq_y[i] != '-':
                return 0
            return 1

        if len(seq_x) != len(seq_y):
            return
        l = len(seq_x)
        ret_insert = self.clf.multi_prepare_predict(
            (seq_x, pos, ann_x, seq_y, pos, ann_y)
            for pos in filter(lambda x: state(x) != 0, xrange(l))
        )
        ret_match = (
            0 for _ in filter(lambda x: state(x) == 0, xrange(l))
        )
        ret = merge(ret_match, ret_insert, (state(x) for x in xrange(l)))
        return ret

    def compute_emissions(self, labels, seq_x, seq_y, ann_x, ann_y):
        classification = self._classification(seq_x, ann_x, seq_y, ann_y)
        data = dict()
        for x in 'ACGT':
            data[x] = list()

        count = 0.0
        for state, x, y, c in zip(labels, seq_x, seq_y, classification):
            # use one insert state for both X and Y - they are equivalent for now
            if state == 'Y':
                state = 'X'
            count += 1
            if state == 'X':
                if x != '-':
                    data[x].append(c)
                if y != '-':
                    data[y].append(c)

        res = dict()
        #todo: move gaussian one level up
        for x in 'ACGT':
            p = len(data[x]) / count
            if len(data[x]) > 1:
                g = gaussian_kde(data[x])
                for c in xrange(precision):
                    res[(x, c)] = p * g.integrate_box(float(c) / precision, float(c + 1.0) / precision)
            else:
                for c in xrange(precision):
                    res[(x, c)] = p / precision
        return res

    def _emission(self, c, seq_x, x, seq_y, y):
        if self.state_label == 'X':
            b = seq_x[x]
        else:
            b = seq_y[y]
        return self.emissions[(b, round((precision - 1) * c))]


