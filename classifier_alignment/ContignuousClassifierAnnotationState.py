from collections import defaultdict
from scipy.stats import gaussian_kde
from classifier_alignment.ClassifierAnnotationState import ClassifierAnnotationState,\
    ClassifierAnnotationIndelState
from hmm.HMMLoader import getInitializerObject
import pickle


def emission_f(s):
    n, g = pickle.loads(s)
    return lambda c: n*g(c)


class ContignuousClassifierAnnotationState(ClassifierAnnotationState):
    def load(self, dictionary):
        ClassifierAnnotationState.load(self, dictionary)
        self.emissions = dict()
        for [key, s] in dictionary["emission"]:
            if key.__class__.__name__ == "list":
                key = tuple(key)
            self.emissions[key] = emission_f(s)

    def _emission(self, c, seq_x, x, seq_y, y):
        return self.emissions[(seq_x[x], seq_y[y])](c)

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
                g = gaussian_kde(data[(x, y)])
                norm = p/g.integrate_box(0, 1)
                emissions[(x, y)] = pickle.dumps((norm, g))

        return emissions


class ContignuousClassifierAnnotationIndelState(ClassifierAnnotationIndelState):
    def load(self, dictionary):
        ClassifierAnnotationIndelState.load(self, dictionary)
        self.emissions = dict()
        for [key, s] in dictionary["emission"]:
            if key.__class__.__name__ == "list":
                key = tuple(key)
            self.emissions[key] = emission_f(s)

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
            g = gaussian_kde(data[x])
            norm = p/g.integrate_box(0, 1)
            emissions[x] = pickle.dumps((norm, g))

        return emissions

    def _emission(self, c, seq_x, x, seq_y, y):
        if self.onechar == 'X':
            b = seq_x[x]
        else:
            b = seq_y[y]
        return self.emissions[b](c)


def register(loader):
    for obj in [ContignuousClassifierAnnotationState, ContignuousClassifierAnnotationIndelState]:
        loader.addFunction(obj.__name__, getInitializerObject(obj, loader.mathType))
