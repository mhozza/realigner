import os
from hack.ClassifierState import ClassifierState, ClassifierIndelState
from hack.DataLoader import DataLoader

precision = 10
pseudocount = 0.001


class ClassifierAnnotationState(ClassifierState):
    def __init__(self, *args, **kwargs):
        ClassifierState.__init__(self, *args, **kwargs)

    def _emission(self, c, seq_x, x, seq_y, y):
        emissions = {
            ('A', 'A', 0): 1.1848116623381514e-07,
            ('A', 'A', 1): 1.1848116623381514e-07,
            ('A', 'A', 2): 1.1848116623381514e-07,
            ('A', 'A', 3): 0.0016588548084396457,
            ('A', 'A', 4): 0.0757095837045741,
            ('A', 'A', 5): 1.1848116623381514e-07,
            ('A', 'A', 6): 1.1848116623381514e-07,
            ('A', 'A', 7): 0.0009479678110367549,
            ('A', 'A', 8): 1.1848116623381514e-07,
            ('A', 'A', 9): 1.1848116623381514e-07,
            ('A', 'C', 0): 1.1848116623381514e-07,
            ('A', 'C', 1): 1.1848116623381514e-07,
            ('A', 'C', 2): 1.1848116623381514e-07,
            ('A', 'C', 3): 0.0007110054785691246,
            ('A', 'C', 4): 0.0529611997876816,
            ('A', 'C', 5): 1.1848116623381514e-07,
            ('A', 'C', 6): 1.1848116623381514e-07,
            ('A', 'C', 7): 1.1848116623381514e-07,
            ('A', 'C', 8): 1.1848116623381514e-07,
            ('A', 'C', 9): 0.0007110054785691246,
            ('A', 'G', 0): 1.1848116623381514e-07,
            ('A', 'G', 1): 1.1848116623381514e-07,
            ('A', 'G', 2): 1.1848116623381514e-07,
            ('A', 'G', 3): 0.0013034113097382003,
            ('A', 'G', 4): 0.0014218924759720154,
            ('A', 'G', 5): 0.05544930427859172,
            ('A', 'G', 6): 1.1848116623381514e-07,
            ('A', 'G', 7): 1.1848116623381514e-07,
            ('A', 'G', 8): 0.0007110054785691246,
            ('A', 'G', 9): 1.1848116623381514e-07,
            ('A', 'T', 0): 1.1848116623381514e-07,
            ('A', 'T', 1): 1.1848116623381514e-07,
            ('A', 'T', 2): 0.001184930143504385,
            ('A', 'T', 3): 0.0005925243123353095,
            ('A', 'T', 4): 0.049999170631836225,
            ('A', 'T', 5): 1.1848116623381514e-07,
            ('A', 'T', 6): 1.1848116623381514e-07,
            ('A', 'T', 7): 1.1848116623381514e-07,
            ('A', 'T', 8): 1.1848116623381514e-07,
            ('A', 'T', 9): 0.0004740431461014943,
            ('C', 'A', 0): 1.1848116623381514e-07,
            ('C', 'A', 1): 1.1848116623381514e-07,
            ('C', 'A', 2): 0.00106644897727057,
            ('C', 'A', 3): 1.1848116623381514e-07,
            ('C', 'A', 4): 0.0014218924759720154,
            ('C', 'A', 5): 0.050947019961706745,
            ('C', 'A', 6): 1.1848116623381514e-07,
            ('C', 'A', 7): 1.1848116623381514e-07,
            ('C', 'A', 8): 0.0007110054785691246,
            ('C', 'A', 9): 1.1848116623381514e-07,
            ('C', 'C', 0): 1.1848116623381514e-07,
            ('C', 'C', 1): 1.1848116623381514e-07,
            ('C', 'C', 2): 0.0015403736422058307,
            ('C', 'C', 3): 0.0015403736422058307,
            ('C', 'C', 4): 1.1848116623381514e-07,
            ('C', 'C', 5): 0.08068579268639434,
            ('C', 'C', 6): 1.1848116623381514e-07,
            ('C', 'C', 7): 1.1848116623381514e-07,
            ('C', 'C', 8): 0.0016588548084396457,
            ('C', 'C', 9): 1.1848116623381514e-07,
            ('C', 'G', 0): 1.1848116623381514e-07,
            ('C', 'G', 1): 1.1848116623381514e-07,
            ('C', 'G', 2): 0.0009479678110367549,
            ('C', 'G', 3): 1.1848116623381514e-07,
            ('C', 'G', 4): 0.0007110054785691246,
            ('C', 'G', 5): 0.0545014549487212,
            ('C', 'G', 6): 1.1848116623381514e-07,
            ('C', 'G', 7): 1.1848116623381514e-07,
            ('C', 'G', 8): 1.1848116623381514e-07,
            ('C', 'G', 9): 0.00035556197986767924,
            ('C', 'T', 0): 1.1848116623381514e-07,
            ('C', 'T', 1): 1.1848116623381514e-07,
            ('C', 'T', 2): 1.1848116623381514e-07,
            ('C', 'T', 3): 0.0007110054785691246,
            ('C', 'T', 4): 0.051894869291577266,
            ('C', 'T', 5): 1.1848116623381514e-07,
            ('C', 'T', 6): 1.1848116623381514e-07,
            ('C', 'T', 7): 1.1848116623381514e-07,
            ('C', 'T', 8): 1.1848116623381514e-07,
            ('C', 'T', 9): 0.0008294866448029397,
            ('G', 'A', 0): 1.1848116623381514e-07,
            ('G', 'A', 1): 1.1848116623381514e-07,
            ('G', 'A', 2): 0.0013034113097382003,
            ('G', 'A', 3): 0.0014218924759720154,
            ('G', 'A', 4): 0.054027530283785936,
            ('G', 'A', 5): 1.1848116623381514e-07,
            ('G', 'A', 6): 0.0005925243123353095,
            ('G', 'A', 7): 1.1848116623381514e-07,
            ('G', 'A', 8): 1.1848116623381514e-07,
            ('G', 'A', 9): 1.1848116623381514e-07,
            ('G', 'C', 0): 1.1848116623381514e-07,
            ('G', 'C', 1): 1.1848116623381514e-07,
            ('G', 'C', 2): 1.1848116623381514e-07,
            ('G', 'C', 3): 1.1848116623381514e-07,
            ('G', 'C', 4): 0.001184930143504385,
            ('G', 'C', 5): 0.05248727512274634,
            ('G', 'C', 6): 0.0008294866448029397,
            ('G', 'C', 7): 1.1848116623381514e-07,
            ('G', 'C', 8): 1.1848116623381514e-07,
            ('G', 'C', 9): 0.0009479678110367549,
            ('G', 'G', 0): 1.1848116623381514e-07,
            ('G', 'G', 1): 1.1848116623381514e-07,
            ('G', 'G', 2): 1.1848116623381514e-07,
            ('G', 'G', 3): 0.003791515800648318,
            ('G', 'G', 4): 0.08127819851756342,
            ('G', 'G', 5): 1.1848116623381514e-07,
            ('G', 'G', 6): 1.1848116623381514e-07,
            ('G', 'G', 7): 1.1848116623381514e-07,
            ('G', 'G', 8): 1.1848116623381514e-07,
            ('G', 'G', 9): 0.0013034113097382003,
            ('G', 'T', 0): 1.1848116623381514e-07,
            ('G', 'T', 1): 1.1848116623381514e-07,
            ('G', 'T', 2): 1.1848116623381514e-07,
            ('G', 'T', 3): 0.0016588548084396457,
            ('G', 'T', 4): 0.053079680953915416,
            ('G', 'T', 5): 1.1848116623381514e-07,
            ('G', 'T', 6): 1.1848116623381514e-07,
            ('G', 'T', 7): 1.1848116623381514e-07,
            ('G', 'T', 8): 0.00023708081363386409,
            ('G', 'T', 9): 1.1848116623381514e-07,
            ('T', 'A', 0): 1.1848116623381514e-07,
            ('T', 'A', 1): 1.1848116623381514e-07,
            ('T', 'A', 2): 1.1848116623381514e-07,
            ('T', 'A', 3): 1.1848116623381514e-07,
            ('T', 'A', 4): 0.002014298307141091,
            ('T', 'A', 5): 0.05035461413053767,
            ('T', 'A', 6): 1.1848116623381514e-07,
            ('T', 'A', 7): 1.1848116623381514e-07,
            ('T', 'A', 8): 0.00106644897727057,
            ('T', 'A', 9): 1.1848116623381514e-07,
            ('T', 'C', 0): 1.1848116623381514e-07,
            ('T', 'C', 1): 1.1848116623381514e-07,
            ('T', 'C', 2): 1.1848116623381514e-07,
            ('T', 'C', 3): 0.00106644897727057,
            ('T', 'C', 4): 1.1848116623381514e-07,
            ('T', 'C', 5): 0.049999170631836225,
            ('T', 'C', 6): 1.1848116623381514e-07,
            ('T', 'C', 7): 1.1848116623381514e-07,
            ('T', 'C', 8): 1.1848116623381514e-07,
            ('T', 'C', 9): 0.0009479678110367549,
            ('T', 'G', 0): 1.1848116623381514e-07,
            ('T', 'G', 1): 1.1848116623381514e-07,
            ('T', 'G', 2): 1.1848116623381514e-07,
            ('T', 'G', 3): 1.1848116623381514e-07,
            ('T', 'G', 4): 0.05461993611495501,
            ('T', 'G', 5): 0.0016588548084396457,
            ('T', 'G', 6): 1.1848116623381514e-07,
            ('T', 'G', 7): 0.0005925243123353095,
            ('T', 'G', 8): 1.1848116623381514e-07,
            ('T', 'G', 9): 1.1848116623381514e-07,
            ('T', 'T', 0): 1.1848116623381514e-07,
            ('T', 'T', 1): 1.1848116623381514e-07,
            ('T', 'T', 2): 1.1848116623381514e-07,
            ('T', 'T', 3): 0.0016588548084396457,
            ('T', 'T', 4): 0.087320737995488,
            ('T', 'T', 5): 1.1848116623381514e-07,
            ('T', 'T', 6): 1.1848116623381514e-07,
            ('T', 'T', 7): 1.1848116623381514e-07,
            ('T', 'T', 8): 1.1848116623381514e-07,
            ('T', 'T', 9): 0.001184930143504385,
        }
        return emissions[(seq_x[x], seq_y[y], round((precision-1)*c))]


class ClassifierAnnotationIndelState(ClassifierIndelState):
    def __init__(self, *args, **kwargs):
        ClassifierIndelState.__init__(self, *args, **kwargs)

    def _emission(self, c, seq_x, x, seq_y, y):
        emissions = {
            ('A', 0): 0.008658951864250263,
            ('A', 1): 1.442918157682097e-06,
            ('A', 2): 1.442918157682097e-06,
            ('A', 3): 1.442918157682097e-06,
            ('A', 4): 0.28281340182384873,
            ('A', 5): 1.442918157682097e-06,
            ('A', 6): 1.442918157682097e-06,
            ('A', 7): 1.442918157682097e-06,
            ('A', 8): 1.442918157682097e-06,
            ('A', 9): 1.442918157682097e-06,
            ('C', 0): 0.010101870021932361,
            ('C', 1): 1.442918157682097e-06,
            ('C', 2): 0.22221083920120063,
            ('C', 3): 1.442918157682097e-06,
            ('C', 4): 1.442918157682097e-06,
            ('C', 5): 1.442918157682097e-06,
            ('C', 6): 1.442918157682097e-06,
            ('C', 7): 1.442918157682097e-06,
            ('C', 8): 1.442918157682097e-06,
            ('C', 9): 1.442918157682097e-06,
            ('G', 0): 0.011544788179614457,
            ('G', 1): 1.442918157682097e-06,
            ('G', 2): 1.442918157682097e-06,
            ('G', 3): 1.442918157682097e-06,
            ('G', 4): 1.442918157682097e-06,
            ('G', 5): 1.442918157682097e-06,
            ('G', 6): 0.197681230520605,
            ('G', 7): 1.442918157682097e-06,
            ('G', 8): 1.442918157682097e-06,
            ('G', 9): 1.442918157682097e-06,
            ('T', 0): 0.014430624494978651,
            ('T', 1): 1.442918157682097e-06,
            ('T', 2): 1.442918157682097e-06,
            ('T', 3): 1.442918157682097e-06,
            ('T', 4): 0.2525121205125247,
            ('T', 5): 1.442918157682097e-06,
            ('T', 6): 1.442918157682097e-06,
            ('T', 7): 1.442918157682097e-06,
            ('T', 8): 1.442918157682097e-06,
            ('T', 9): 1.442918157682097e-06,
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
