import os
from classifier_alignment.ClassifierState import ClassifierState, ClassifierIndelState
from classifier_alignment.DataLoader import DataLoader

precision = 10
pseudocount = 0.001


class ClassifierAnnotationState(ClassifierState):
    def __init__(self, *args, **kwargs):
        ClassifierState.__init__(self, *args, **kwargs)

    def _emission(self, c, seq_x, x, seq_y, y):
        emissions = {
            ('A', 'A', 0): 1.219339703163939e-07,
            ('A', 'A', 1): 1.219339703163939e-07,
            ('A', 'A', 2): 0.013412858668773646,
            ('A', 'A', 3): 1.219339703163939e-07,
            ('A', 'A', 4): 1.219339703163939e-07,
            ('A', 'A', 5): 1.219339703163939e-07,
            ('A', 'A', 6): 0.13266428163820687,
            ('A', 'A', 7): 1.219339703163939e-07,
            ('A', 'A', 8): 1.219339703163939e-07,
            ('A', 'A', 9): 0.0008536597261850735,
            ('A', 'C', 0): 0.0031704051621965572,
            ('A', 'C', 1): 1.219339703163939e-07,
            ('A', 'C', 2): 1.219339703163939e-07,
            ('A', 'C', 3): 0.03121521833496715,
            ('A', 'C', 4): 1.219339703163939e-07,
            ('A', 'C', 5): 1.219339703163939e-07,
            ('A', 'C', 6): 0.0004878578152358919,
            ('A', 'C', 7): 1.219339703163939e-07,
            ('A', 'C', 8): 1.219339703163939e-07,
            ('A', 'C', 9): 1.219339703163939e-07,
            ('A', 'G', 0): 0.0031704051621965572,
            ('A', 'G', 1): 1.219339703163939e-07,
            ('A', 'G', 2): 1.219339703163939e-07,
            ('A', 'G', 3): 0.03182488818654912,
            ('A', 'G', 4): 1.219339703163939e-07,
            ('A', 'G', 5): 1.219339703163939e-07,
            ('A', 'G', 6): 0.00036592384491949807,
            ('A', 'G', 7): 1.219339703163939e-07,
            ('A', 'G', 8): 1.219339703163939e-07,
            ('A', 'G', 9): 1.219339703163939e-07,
            ('A', 'T', 0): 0.0026826692809309815,
            ('A', 'T', 1): 1.219339703163939e-07,
            ('A', 'T', 2): 1.219339703163939e-07,
            ('A', 'T', 3): 0.02865460495832288,
            ('A', 'T', 4): 1.219339703163939e-07,
            ('A', 'T', 5): 1.219339703163939e-07,
            ('A', 'T', 6): 1.219339703163939e-07,
            ('A', 'T', 7): 0.00024398987460310417,
            ('A', 'T', 8): 1.219339703163939e-07,
            ('A', 'T', 9): 1.219339703163939e-07,
            ('C', 'A', 0): 0.003536207073145739,
            ('C', 'A', 1): 1.219339703163939e-07,
            ('C', 'A', 2): 1.219339703163939e-07,
            ('C', 'A', 3): 0.033288095830345844,
            ('C', 'A', 4): 1.219339703163939e-07,
            ('C', 'A', 5): 1.219339703163939e-07,
            ('C', 'A', 6): 1.219339703163939e-07,
            ('C', 'A', 7): 1.219339703163939e-07,
            ('C', 'A', 8): 1.219339703163939e-07,
            ('C', 'A', 9): 1.219339703163939e-07,
            ('C', 'C', 0): 1.219339703163939e-07,
            ('C', 'C', 1): 1.219339703163939e-07,
            ('C', 'C', 2): 0.015363802193835947,
            ('C', 'C', 3): 1.219339703163939e-07,
            ('C', 'C', 4): 1.219339703163939e-07,
            ('C', 'C', 5): 1.219339703163939e-07,
            ('C', 'C', 6): 1.219339703163939e-07,
            ('C', 'C', 7): 0.13254234766789047,
            ('C', 'C', 8): 1.219339703163939e-07,
            ('C', 'C', 9): 0.0007317257558686796,
            ('C', 'G', 0): 0.003658141043462133,
            ('C', 'G', 1): 1.219339703163939e-07,
            ('C', 'G', 2): 1.219339703163939e-07,
            ('C', 'G', 3): 0.028166869077057306,
            ('C', 'G', 4): 1.219339703163939e-07,
            ('C', 'G', 5): 1.219339703163939e-07,
            ('C', 'G', 6): 0.00036592384491949807,
            ('C', 'G', 7): 1.219339703163939e-07,
            ('C', 'G', 8): 1.219339703163939e-07,
            ('C', 'G', 9): 1.219339703163939e-07,
            ('C', 'T', 0): 0.0012194616371342553,
            ('C', 'T', 1): 0.0015852635480834369,
            ('C', 'T', 2): 1.219339703163939e-07,
            ('C', 'T', 3): 0.029142340839588457,
            ('C', 'T', 4): 1.219339703163939e-07,
            ('C', 'T', 5): 1.219339703163939e-07,
            ('C', 'T', 6): 0.00012205590428671027,
            ('C', 'T', 7): 1.219339703163939e-07,
            ('C', 'T', 8): 1.219339703163939e-07,
            ('C', 'T', 9): 1.219339703163939e-07,
            ('G', 'A', 0): 1.219339703163939e-07,
            ('G', 'A', 1): 0.0025607353106145876,
            ('G', 'A', 2): 1.219339703163939e-07,
            ('G', 'A', 3): 0.024630783937881883,
            ('G', 'A', 4): 1.219339703163939e-07,
            ('G', 'A', 5): 1.219339703163939e-07,
            ('G', 'A', 6): 0.00012205590428671027,
            ('G', 'A', 7): 1.219339703163939e-07,
            ('G', 'A', 8): 1.219339703163939e-07,
            ('G', 'A', 9): 1.219339703163939e-07,
            ('G', 'C', 0): 0.003414273102829345,
            ('G', 'C', 1): 1.219339703163939e-07,
            ('G', 'C', 2): 1.219339703163939e-07,
            ('G', 'C', 3): 0.0282888030473737,
            ('G', 'C', 4): 1.219339703163939e-07,
            ('G', 'C', 5): 1.219339703163939e-07,
            ('G', 'C', 6): 1.219339703163939e-07,
            ('G', 'C', 7): 0.00012205590428671027,
            ('G', 'C', 8): 1.219339703163939e-07,
            ('G', 'C', 9): 1.219339703163939e-07,
            ('G', 'G', 0): 1.219339703163939e-07,
            ('G', 'G', 1): 1.219339703163939e-07,
            ('G', 'G', 2): 0.014144462490672008,
            ('G', 'G', 3): 1.219339703163939e-07,
            ('G', 'G', 4): 1.219339703163939e-07,
            ('G', 'G', 5): 1.219339703163939e-07,
            ('G', 'G', 6): 1.219339703163939e-07,
            ('G', 'G', 7): 0.145711216462061,
            ('G', 'G', 8): 1.219339703163939e-07,
            ('G', 'G', 9): 0.001463329577767043,
            ('G', 'T', 0): 0.0021949333996654063,
            ('G', 'T', 1): 1.219339703163939e-07,
            ('G', 'T', 2): 1.219339703163939e-07,
            ('G', 'T', 3): 0.02767913319579173,
            ('G', 'T', 4): 1.219339703163939e-07,
            ('G', 'T', 5): 1.219339703163939e-07,
            ('G', 'T', 6): 0.00024398987460310417,
            ('G', 'T', 7): 1.219339703163939e-07,
            ('G', 'T', 8): 1.219339703163939e-07,
            ('G', 'T', 9): 1.219339703163939e-07,
            ('T', 'A', 0): 1.219339703163939e-07,
            ('T', 'A', 1): 0.0025607353106145876,
            ('T', 'A', 2): 1.219339703163939e-07,
            ('T', 'A', 3): 0.02853267098800649,
            ('T', 'A', 4): 1.219339703163939e-07,
            ('T', 'A', 5): 1.219339703163939e-07,
            ('T', 'A', 6): 1.219339703163939e-07,
            ('T', 'A', 7): 1.219339703163939e-07,
            ('T', 'A', 8): 1.219339703163939e-07,
            ('T', 'A', 9): 1.219339703163939e-07,
            ('T', 'C', 0): 1.219339703163939e-07,
            ('T', 'C', 1): 0.004145876924727708,
            ('T', 'C', 2): 1.219339703163939e-07,
            ('T', 'C', 3): 0.02865460495832288,
            ('T', 'C', 4): 1.219339703163939e-07,
            ('T', 'C', 5): 1.219339703163939e-07,
            ('T', 'C', 6): 1.219339703163939e-07,
            ('T', 'C', 7): 1.219339703163939e-07,
            ('T', 'C', 8): 1.219339703163939e-07,
            ('T', 'C', 9): 1.219339703163939e-07,
            ('T', 'G', 0): 0.0021949333996654063,
            ('T', 'G', 1): 1.219339703163939e-07,
            ('T', 'G', 2): 1.219339703163939e-07,
            ('T', 'G', 3): 0.030361680542752397,
            ('T', 'G', 4): 1.219339703163939e-07,
            ('T', 'G', 5): 1.219339703163939e-07,
            ('T', 'G', 6): 0.00012205590428671027,
            ('T', 'G', 7): 1.219339703163939e-07,
            ('T', 'G', 8): 1.219339703163939e-07,
            ('T', 'G', 9): 1.219339703163939e-07,
            ('T', 'T', 0): 1.219339703163939e-07,
            ('T', 'T', 1): 1.219339703163939e-07,
            ('T', 'T', 2): 0.017558613659531038,
            ('T', 'T', 3): 1.219339703163939e-07,
            ('T', 'T', 4): 1.219339703163939e-07,
            ('T', 'T', 5): 1.219339703163939e-07,
            ('T', 'T', 6): 0.1358345648664331,
            ('T', 'T', 7): 1.219339703163939e-07,
            ('T', 'T', 8): 1.219339703163939e-07,
            ('T', 'T', 9): 0.0009755936965014675,
        }
        return emissions[(seq_x[x], seq_y[y], round((precision-1)*c))]


class ClassifierAnnotationIndelState(ClassifierIndelState):
    def __init__(self, *args, **kwargs):
        ClassifierIndelState.__init__(self, *args, **kwargs)

    def _emission(self, c, seq_x, x, seq_y, y):
        emissions = {
            ('A', 0): 1.2657586957622411e-06,
            ('A', 1): 1.2657586957622411e-06,
            ('A', 2): 1.2657586957622411e-06,
            ('A', 3): 1.2657586957622411e-06,
            ('A', 4): 0.045568578806136434,
            ('A', 5): 0.2075856918637033,
            ('A', 6): 1.2657586957622411e-06,
            ('A', 7): 1.2657586957622411e-06,
            ('A', 8): 1.2657586957622411e-06,
            ('A', 9): 1.2657586957622411e-06,
            ('C', 0): 1.2657586957622411e-06,
            ('C', 1): 1.2657586957622411e-06,
            ('C', 2): 1.2657586957622411e-06,
            ('C', 3): 1.2657586957622411e-06,
            ('C', 4): 0.03923978532732523,
            ('C', 5): 0.21771176142980123,
            ('C', 6): 1.2657586957622411e-06,
            ('C', 7): 1.2657586957622411e-06,
            ('C', 8): 1.2657586957622411e-06,
            ('C', 9): 1.2657586957622411e-06,
            ('G', 0): 1.2657586957622411e-06,
            ('G', 1): 1.2657586957622411e-06,
            ('G', 2): 1.2657586957622411e-06,
            ('G', 3): 1.2657586957622411e-06,
            ('G', 4): 0.027847957065465063,
            ('G', 5): 0.19872538099336762,
            ('G', 6): 1.2657586957622411e-06,
            ('G', 7): 1.2657586957622411e-06,
            ('G', 8): 1.2657586957622411e-06,
            ('G', 9): 1.2657586957622411e-06,
            ('T', 0): 1.2657586957622411e-06,
            ('T', 1): 1.2657586957622411e-06,
            ('T', 2): 1.2657586957622411e-06,
            ('T', 3): 1.2657586957622411e-06,
            ('T', 4): 0.030379474456989543,
            ('T', 5): 0.2329008657789481,
            ('T', 6): 1.2657586957622411e-06,
            ('T', 7): 1.2657586957622411e-06,
            ('T', 8): 1.2657586957622411e-06,
            ('T', 9): 1.2657586957622411e-06,
        }
        if self.state_label == 'X':
            b = seq_x[x]
        else:
            b = seq_y[y]

        return emissions[(b, round((precision-1)*c))]


class SupervisedHmmClassifierAnnotationStateTraining():
    def __init__(self):
        pass

    def transitions(self, seq_x, seq_y):
        labels = list(self.labels(seq_x, seq_y))

        counts = dict()
        for state in 'MXY':
            counts[state] = dict()
            for nextstate in 'MXY':
                counts[state][nextstate] = 0

        for i, state in enumerate(labels):
            if seq_x[i] == '-' and seq_y[i] == '-':
                continue
            j = i + 1
            while j < len(labels) and seq_x[i] == '-' and seq_y[i] == '-':
                j += 1
            if i < j < len(labels):
                nextstate = labels[j]
                counts[state][nextstate] += 1

        for state in 'MXY':
            s = float(sum(counts[state].values()))
            for nextstate in 'MXY':
                counts[state][nextstate] /= s

        return {
            k+k2: v2 for k, v in counts.iteritems() for k2, v2 in v.iteritems()
        }

    def emissions(self, seq_x, seq_y, ann_x, ann_y):
        labels = self.labels(seq_x, seq_y)
        classification = self.classification(seq_x, ann_x, seq_y, ann_y)
        counts = dict()
        for state in 'MXY':
            counts[state] = dict()
            for x in 'ACGT':
                if state == 'M':
                    for y in 'ACGT':
                        for c in xrange(precision):
                            counts[state][(x, y, c)] = pseudocount
                else:
                    for c in xrange(precision):
                        counts[state][(x, c)] = pseudocount

        for state, x, y, c in zip(labels, seq_x, seq_y, classification):
            if state == 'X':
                if x != '-':
                    counts[state][(x, round((precision-1)*c))] += 1
            elif state == 'Y':
                if y != '-':
                    counts[state][(y, round((precision-1)*c))] += 1
            else:
                counts[state][(x, y, round((precision-1)*c))] += 1

        for state in 'MXY':
            s = float(sum(counts[state].values()))
            for x in 'ACGT':
                if state == 'M':
                    for y in 'ACGT':
                        for c in xrange(precision):
                            counts[state][(x, y, c)] /= s
                else:
                    for c in xrange(precision):
                        counts[state][(x, c)] /= s

        return counts

    def starting(self):
        return [1/3.0, 1/3.0, 1/3.0]

    def get_probabilities(self, seq_x, ann_x, seq_y, ann_y):
        return\
            self.starting(),\
            self.transitions(seq_x, seq_y),\
            self.emissions(seq_x, seq_y, ann_x, ann_y)

    def labels(self, seq_x, seq_y):
        def state(i):
            if seq_x[i] == '-':
                return 'Y'
            if seq_y[i] == '-':
                return 'X'
            return 'M'

        if len(seq_x) != len(seq_y):
            return
        return (state(i) for i in xrange(len(seq_x)))

    def classification(self, seq_x, ann_x, seq_y, ann_y):
        def state(i):
            if seq_x[i] == '-':
                return 'Y'
            if seq_y[i] == '-':
                return 'X'
            return 'M'

        def merge(first, second, rule):
            l = list()
            p1 = 0
            p2 = 0
            for r in rule:
                if state(r) == 'M':
                    l.append(first[p1])
                    p1 += 1
                else:
                    l.append(second[p2])
                    p2 += 1
            return l

        if len(seq_x) != len(seq_y):
            return

        clf_match = ClassifierAnnotationState().clf
        ret_match = clf_match.multi_prepare_predict(
            (seq_x, pos, ann_x, seq_y, pos, ann_y)
            for pos in filter(lambda x: state(x) == 'M', xrange(len(seq_x)))
        )

        clf_insert = ClassifierAnnotationIndelState().clf
        ret_insert = clf_insert.multi_prepare_predict(
            (seq_x, pos, ann_x, seq_y, pos, ann_y)
            for pos in filter(lambda x: state(x) != 'M', xrange(len(seq_x)))
        )

        ret = merge(ret_match, ret_insert, xrange(len(seq_x)))

        return ret


def main():
    path_to_data = "data/"

    dl = DataLoader()
    _, s_x, a_x, s_y, a_y = dl.loadSequence(
        os.path.join(path_to_data, 'train_sequences/simulated_alignment.fa')
    )
    training = SupervisedHmmClassifierAnnotationStateTraining()
    probabilities = training.get_probabilities(s_x, a_x, s_y, a_y)
    print(probabilities)


if __name__ == "__main__":
    main()
