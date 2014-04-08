from collections import defaultdict
from scipy.stats import norm, gaussian_kde
from classifier_alignment.ClassifierState import ClassifierState, ClassifierIndelState
from tools.utils import merge
import numpy
from numpy.linalg.linalg import LinAlgError

precision = 10
#pseudocount = 0.001 # Fixme toto by sa mohlo zacat pouzivat


class ClassifierAnnotationState(ClassifierState):
    def __init__(self, *args, **kwargs):
        ClassifierState.__init__(self, *args, **kwargs)

    def _emission(self, c, seq_x, x, seq_y, y):
        return self.emissions[(seq_x[x], seq_y[y], round((precision - 1) * float(c)))]

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

        ret = merge((state(x) for x in xrange(l)), ret_match, ret_insert)
        return ret

    def compute_emissions(self, labels, seq_x, seq_y, ann_x, ann_y):
        classification = self._classification(seq_x, ann_x, seq_y, ann_y)
        data = defaultdict(list)
        count = 0.0
        for label, x, y, c in zip(labels, seq_x, seq_y, classification):
            if label == 'M':
                count += 2.0
                data[(x, y)].append(c)
                data[(y, x)].append(c)

        emissions = dict()
        # todo: move gaussian one level up?
        for x in 'ACGT':
            for y in 'ACGT':
                p = len(data[(x, y)]) / count
                if len(data[(x, y)]) > 1:
                    try:
                        g = gaussian_kde(data[(x, y)])
                        for c in xrange(precision):
                            # print c, float(c) / precision, float(c + 1.0) / precision
                            emissions[(x, y, c)] = p * g.integrate_box(
                                float(c) / precision, float(c + 1.0) / precision
                            )
                    except LinAlgError:
                        hist, _ = numpy.histogram(
                            data[(x, y)], precision, density=True, range=(0,1)
                        )
                        for c in xrange(precision):
                            emissions[(x, y, c)] = p * hist[c]/precision
                else:
                    for c in xrange(precision):
                        emissions[(x, y, c)] = p / precision
        return emissions, count


class ClassifierAnnotationIndelState(ClassifierIndelState):
    def __init__(self, *args, **kwargs):
        ClassifierIndelState.__init__(self, *args, **kwargs)

    def _classification(self, seq_x, ann_x, seq_y, ann_y):
        def state(i):
            if seq_x[i] == '-' and seq_y !='-':
                return 2
            if seq_y[i] == '-' and seq_x !='-':
                return 1
            return 0

        if len(seq_x) != len(seq_y):
            return
        l = len(seq_x)

        ret_match = (
            0 for _ in filter(lambda x: state(x) == 0, xrange(l))
        )

        ret_insertX = self.clf.multi_prepare_predict(
            (seq_x, pos, ann_x, seq_y, pos, ann_y)
            for pos in filter(lambda x: state(x) == 1, xrange(l))
        )

        ret_insertY = self.clf.multi_prepare_predict(
            (seq_y, pos, ann_y, seq_x, pos, ann_x)
            for pos in filter(lambda x: state(x) == 2, xrange(l))
        )

        # for (i, v), p in zip(enumerate(ret_insertX), filter(lambda x: state(x) == 1, xrange(l))):
        #     print i, v, state(p), seq_x[p], seq_y[p], p
        # print ret_insertY

        ret = merge((state(x) for x in xrange(l)), ret_match, ret_insertX, ret_insertY)
        return ret

    def compute_emissions(self, labels, seq_x, seq_y, ann_x, ann_y):
        classification = self._classification(seq_x, ann_x, seq_y, ann_y)
        data = defaultdict(list)
        count = 0.0
        for state, x, y, c in zip(labels, seq_x, seq_y, classification):
            if state == 'X':
                count += 1
                data[x].append(c)
            if state == 'Y':
                count += 1
                data[y].append(c)

        emissions = dict()
        #todo: move gaussian one level up?
        for x in 'ACGT':
            p = len(data[x]) / count
            # print len(data[x]), count, p
            if len(data[x]) > 1:
                # try:
                #     g = gaussian_kde(data[x])
                #     for c in xrange(precision):
                #         emissions[(x, c)] = p * g.integrate_box(
                #             float(c) / precision, float(c + 1.0) / precision
                #         )
                #         print c, emissions[(x, c)]
                # except LinAlgError:
                hist, _ = numpy.histogram(
                    data[x], bins=precision, range=(0.0, 1.0), density=True
                )
                # print hist
                for c in xrange(precision):
                    # print c, p * hist[c] / precision
                    emissions[(x, c)] = p * hist[c] / precision
            else:
                for c in xrange(precision):
                    emissions[(x, c)] = p / precision
        return emissions, count

    def _emission(self, c, seq_x, x, seq_y, y):
        if self.onechar == 'X':
            b = seq_x[x]
        else:
            b = seq_y[y]
        return self.emissions[(b, round((precision - 1) * float(c)))]


