from collections import defaultdict
from scipy.stats import gaussian_kde
from alignment import Fasta
from classifier_alignment.ClassifierState import ClassifierState, ClassifierIndelState
from hmm.HMMLoader import getInitializerObject
from tools.utils import merge
import numpy
from numpy.linalg.linalg import LinAlgError
# from classifier_alignment import plot_utils

precision = 10
use_gaussian = True
#pseudocount = 0.001 # Fixme toto by sa mohlo zacat pouzivat


def hist_preprocessor(p, data):
    hist, _ = numpy.histogram(data, precision, density=True, range=(0, 1))
    return lambda c: p * hist[c] / precision


def gaussian_preprocessor(p, data):
    try:
        g = gaussian_kde(data)
        c_norm = g.integrate_box(0, 1)
    except LinAlgError:
        return hist_preprocessor(p, data)

    return lambda c: p/c_norm * g.integrate_box(
        float(c) / precision, float(c + 1.0) / precision
    )


def constant_preprocessor(p):
    return lambda _: p / precision


class ClassifierAnnotationState(ClassifierState):
    def __init__(self, *args, **kwargs):
        ClassifierState.__init__(self, *args, **kwargs)

    def _emission(self, c, seq_x, x, seq_y, y):
        return self.emissions[(seq_x[x], seq_y[y], round((precision - 1) * float(c)))]

    def _classification(self, sequence_x, ann_x, sequence_y, ann_y):
        def state(i):
                if sequence_x[i] == '-' and sequence_y[i] == '-':
                    return 1
                if sequence_x[i] == '-':
                    return 1
                if sequence_y[i] == '-':
                    return 1
                return 0

        def get_pos():
            def state(i):
                if sequence_x[i] == '-' and sequence_y[i] == '-':
                    return -1
                if sequence_x[i] == '-':
                    return 2
                if sequence_y[i] == '-':
                    return 1
                return 0

            pos_x, pos_y = 0, 0
            pos = list()
            for i in xrange(l):
                pos.append((pos_x, pos_y))
                s = state(i)
                if s == 0:
                    pos_x += 1
                    pos_y += 1
                if s == 1:
                    pos_x += 1
                if s == 2:
                    pos_y += 1

            return pos

        assert len(sequence_y) == len(sequence_x)
        l = len(sequence_x)

        sequence_xs = Fasta.alnToSeq(sequence_x)
        sequence_ys = Fasta.alnToSeq(sequence_y)

        positions = get_pos()

        ret_match = self.clf.multi_prepare_predict(
            (sequence_xs, positions[pos][0], ann_x, sequence_ys, positions[pos][1], ann_y)
            for pos in filter(lambda x: state(x) == 0, xrange(l))
        )

        ret_insert = (
            0 for _ in filter(lambda x: state(x) != 0, xrange(l))
        )

        ret = merge((state(x) for x in xrange(l)), ret_match, ret_insert)
        return ret

    #deprecated:
    # def compute_emissions(self, labels, seq_x, seq_y, ann_x, ann_y):
    #     return self.compute_emissions_multi([(labels, seq_x, seq_y, ann_x, ann_y)])

    def compute_emissions_multi(self, sequences):
        data = defaultdict(list)
        count = 0.0
        for labels, seq_x, seq_y, ann_x, ann_y in sequences:
            classification = self._classification(seq_x, ann_x, seq_y, ann_y)
            for label, x, y, c in zip(labels, seq_x, seq_y, classification):
                if label == 'M':
                    count += 2.0
                    data[(x, y)].append(c)
                    data[(y, x)].append(c)

        emissions = dict()
        for x in 'ACGT':
            for y in 'ACGT':
                p = len(data[(x, y)]) / count

                if len(data[(x, y)]) > 1:
                    # plot_utils.plot3(*compute_graph_data3(data[x, y]))
                    if use_gaussian:
                        preprocessor = gaussian_preprocessor(p, data[(x, y)])
                    else:
                        preprocessor = hist_preprocessor(p, data[(x, y)])
                else:
                    preprocessor = constant_preprocessor(p)

                for c in xrange(precision):
                    emissions[(x, y, c)] = preprocessor(c)

        return emissions


class ClassifierAnnotationIndelState(ClassifierIndelState):
    def __init__(self, *args, **kwargs):
        ClassifierIndelState.__init__(self, *args, **kwargs)

    def _classification(self, sequence_x, ann_x, sequence_y, ann_y):
        def state(i):
            if sequence_x[i] == '-' and sequence_y[i] == '-':
                return 0
            if sequence_x[i] == '-':
                return 2
            if sequence_y[i] == '-':
                return 1
            return 0

        def get_pos():
            def state(i):
                if sequence_x[i] == '-' and sequence_y[i] == '-':
                    return -1
                if sequence_x[i] == '-':
                    return 2
                if sequence_y[i] == '-':
                    return 1
                return 0

            pos_x, pos_y = 0, 0
            pos = list()
            for i in xrange(len(sequence_x)):
                pos.append((pos_x, pos_y))
                s = state(i)
                if s == 0:
                    pos_x += 1
                    pos_y += 1
                if s == 1:
                    pos_x += 1
                if s == 2:
                    pos_y += 1

            return pos

        assert len(sequence_y) == len(sequence_x)
        l = len(sequence_x)

        sequence_xs = Fasta.alnToSeq(sequence_x)
        sequence_ys = Fasta.alnToSeq(sequence_y)

        positions = get_pos()

        ret_match = (
            0 for _ in filter(lambda x: state(x) == 0, xrange(l))
        )

        ret_insertX = self.clf.multi_prepare_predict(
            (sequence_xs, positions[pos][0], ann_x, sequence_ys, positions[pos][1], ann_y)
            for pos in filter(lambda x: state(x) == 1, xrange(l))
        )

        ret_insertY = self.clf.multi_prepare_predict(
            (sequence_ys, positions[pos][1], ann_y, sequence_xs, positions[pos][0], ann_x)
            for pos in filter(lambda x: state(x) == 2, xrange(l))
        )

        ret = merge((state(x) for x in xrange(l)), ret_match, ret_insertX, ret_insertY)
        return ret

    #deprecated:
    # def compute_emissions(self, labels, seq_x, seq_y, ann_x, ann_y):
    #     return self.compute_emissions_multi([(labels, seq_x, seq_y, ann_x, ann_y)])

    def compute_emissions_multi(self, sequences):
        data = defaultdict(list)
        count = 0.0

        for labels, seq_x, seq_y, ann_x, ann_y in sequences:
            classification = self._classification(seq_x, ann_x, seq_y, ann_y)
            for state, x, y, c in zip(labels, seq_x, seq_y, classification):
                if state == 'X':
                    count += 1
                    data[x].append(c)
                if state == 'Y':
                    count += 1
                    data[y].append(c)

        emissions = dict()
        for x in 'ACGT':
            p = len(data[x]) / count
            if len(data[x]) > 1:
                # plot_utils.plot3(*compute_graph_data3(data[x]))
                if use_gaussian:
                    preprocessor = gaussian_preprocessor(p, data[x])
                else:
                    preprocessor = hist_preprocessor(p, data[x])
            else:
                preprocessor = constant_preprocessor(p)

            for c in xrange(precision):
                emissions[(x, c)] = preprocessor(c)
                # print x, c, emissions[(x, c)]

        return emissions

    def _emission(self, c, seq_x, x, seq_y, y):
        if self.onechar == 'X':
            b = seq_x[x]
        else:
            b = seq_y[y]
        return self.emissions[(b, round((precision - 1) * float(c)))]


def register(loader):
    for obj in [ClassifierAnnotationState, ClassifierAnnotationIndelState]:
        loader.addFunction(obj.__name__, getInitializerObject(obj, loader.mathType))


def compute_graph_data(data):
    print len(data)
    hist, _ = numpy.histogram(data, bins=precision, range=(0.0, 1.0), density=True)
    print hist
    g = gaussian_kde(data)
    return hist, g


def compute_graph_data3(data):
    # print len(data)
    # with open('data{}.dat'.format(len(data)), 'w') as f:
    #     f.write(str(data))
    hist, _ = numpy.histogram(data, bins=precision, range=(0.0, 1.0), density=True)
    # print hist
    g = gaussian_kde(data)
    gp = gaussian_preprocessor(1, data)
    h2 = [gp(c) for c in xrange(precision)]
    return hist, g, h2
