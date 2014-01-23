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
            ('A', 'A', 0): 1.1680059801906213e-06,
            ('A', 'A', 1): 1.1680059801906213e-06,
            ('A', 'A', 2): 0.03504134741169883,
            ('A', 'A', 3): 1.1680059801906213e-06,
            ('A', 'A', 4): 1.1680059801906213e-06,
            ('A', 'A', 5): 1.1680059801906213e-06,
            ('A', 'A', 6): 1.1680059801906213e-06,
            ('A', 'A', 7): 0.12964983180713918,
            ('A', 'A', 8): 1.1680059801906213e-06,
            ('A', 'A', 9): 0.011681227807886404,
            ('A', 'C', 0): 0.005841197906933297,
            ('A', 'C', 1): 1.1680059801906213e-06,
            ('A', 'C', 2): 1.1680059801906213e-06,
            ('A', 'C', 3): 0.022193281629601994,
            ('A', 'C', 4): 1.1680059801906213e-06,
            ('A', 'C', 5): 1.1680059801906213e-06,
            ('A', 'C', 6): 1.1680059801906213e-06,
            ('A', 'C', 7): 1.1680059801906213e-06,
            ('A', 'C', 8): 1.1680059801906213e-06,
            ('A', 'C', 9): 1.1680059801906213e-06,
            ('A', 'G', 0): 0.0035051859465520547,
            ('A', 'G', 1): 1.1680059801906213e-06,
            ('A', 'G', 2): 1.1680059801906213e-06,
            ('A', 'G', 3): 0.02569729957017386,
            ('A', 'G', 4): 1.1680059801906213e-06,
            ('A', 'G', 5): 1.1680059801906213e-06,
            ('A', 'G', 6): 1.1680059801906213e-06,
            ('A', 'G', 7): 1.1680059801906213e-06,
            ('A', 'G', 8): 1.1680059801906213e-06,
            ('A', 'G', 9): 1.1680059801906213e-06,
            ('A', 'T', 0): 0.002337179966361433,
            ('A', 'T', 1): 1.1680059801906213e-06,
            ('A', 'T', 2): 1.1680059801906213e-06,
            ('A', 'T', 3): 0.02569729957017386,
            ('A', 'T', 4): 1.1680059801906213e-06,
            ('A', 'T', 5): 1.1680059801906213e-06,
            ('A', 'T', 6): 1.1680059801906213e-06,
            ('A', 'T', 7): 0.002337179966361433,
            ('A', 'T', 8): 1.1680059801906213e-06,
            ('A', 'T', 9): 1.1680059801906213e-06,
            ('C', 'A', 0): 0.0035051859465520547,
            ('C', 'A', 1): 1.1680059801906213e-06,
            ('C', 'A', 2): 1.1680059801906213e-06,
            ('C', 'A', 3): 0.023361287609792617,
            ('C', 'A', 4): 1.1680059801906213e-06,
            ('C', 'A', 5): 1.1680059801906213e-06,
            ('C', 'A', 6): 1.1680059801906213e-06,
            ('C', 'A', 7): 0.002337179966361433,
            ('C', 'A', 8): 1.1680059801906213e-06,
            ('C', 'A', 9): 1.1680059801906213e-06,
            ('C', 'C', 0): 1.1680059801906213e-06,
            ('C', 'C', 1): 1.1680059801906213e-06,
            ('C', 'C', 2): 0.0280333115305551,
            ('C', 'C', 3): 1.1680059801906213e-06,
            ('C', 'C', 4): 1.1680059801906213e-06,
            ('C', 'C', 5): 1.1680059801906213e-06,
            ('C', 'C', 6): 0.10862572416370798,
            ('C', 'C', 7): 1.1680059801906213e-06,
            ('C', 'C', 8): 1.1680059801906213e-06,
            ('C', 'C', 9): 0.010513221827695783,
            ('C', 'G', 0): 0.002337179966361433,
            ('C', 'G', 1): 0.0035051859465520547,
            ('C', 'G', 2): 1.1680059801906213e-06,
            ('C', 'G', 3): 0.023361287609792617,
            ('C', 'G', 4): 1.1680059801906213e-06,
            ('C', 'G', 5): 1.1680059801906213e-06,
            ('C', 'G', 6): 0.0011691739861708118,
            ('C', 'G', 7): 1.1680059801906213e-06,
            ('C', 'G', 8): 1.1680059801906213e-06,
            ('C', 'G', 9): 1.1680059801906213e-06,
            ('C', 'T', 0): 0.002337179966361433,
            ('C', 'T', 1): 1.1680059801906213e-06,
            ('C', 'T', 2): 1.1680059801906213e-06,
            ('C', 'T', 3): 0.01868926368903013,
            ('C', 'T', 4): 1.1680059801906213e-06,
            ('C', 'T', 5): 1.1680059801906213e-06,
            ('C', 'T', 6): 0.0011691739861708118,
            ('C', 'T', 7): 1.1680059801906213e-06,
            ('C', 'T', 8): 1.1680059801906213e-06,
            ('C', 'T', 9): 1.1680059801906213e-06,
            ('G', 'A', 0): 0.0035051859465520547,
            ('G', 'A', 1): 1.1680059801906213e-06,
            ('G', 'A', 2): 1.1680059801906213e-06,
            ('G', 'A', 3): 0.03270533545131759,
            ('G', 'A', 4): 1.1680059801906213e-06,
            ('G', 'A', 5): 1.1680059801906213e-06,
            ('G', 'A', 6): 1.1680059801906213e-06,
            ('G', 'A', 7): 0.0011691739861708118,
            ('G', 'A', 8): 1.1680059801906213e-06,
            ('G', 'A', 9): 1.1680059801906213e-06,
            ('G', 'C', 0): 1.1680059801906213e-06,
            ('G', 'C', 1): 1.1680059801906213e-06,
            ('G', 'C', 2): 1.1680059801906213e-06,
            ('G', 'C', 3): 0.024529293589983237,
            ('G', 'C', 4): 1.1680059801906213e-06,
            ('G', 'C', 5): 1.1680059801906213e-06,
            ('G', 'C', 6): 1.1680059801906213e-06,
            ('G', 'C', 7): 1.1680059801906213e-06,
            ('G', 'C', 8): 1.1680059801906213e-06,
            ('G', 'C', 9): 1.1680059801906213e-06,
            ('G', 'G', 0): 1.1680059801906213e-06,
            ('G', 'G', 1): 1.1680059801906213e-06,
            ('G', 'G', 2): 0.021025275649411375,
            ('G', 'G', 3): 1.1680059801906213e-06,
            ('G', 'G', 4): 1.1680059801906213e-06,
            ('G', 'G', 5): 1.1680059801906213e-06,
            ('G', 'G', 6): 0.10278569426275488,
            ('G', 'G', 7): 1.1680059801906213e-06,
            ('G', 'G', 8): 1.1680059801906213e-06,
            ('G', 'G', 9): 0.01635325172864889,
            ('G', 'T', 0): 0.002337179966361433,
            ('G', 'T', 1): 1.1680059801906213e-06,
            ('G', 'T', 2): 1.1680059801906213e-06,
            ('G', 'T', 3): 0.0280333115305551,
            ('G', 'T', 4): 1.1680059801906213e-06,
            ('G', 'T', 5): 1.1680059801906213e-06,
            ('G', 'T', 6): 0.004673191926742676,
            ('G', 'T', 7): 1.1680059801906213e-06,
            ('G', 'T', 8): 1.1680059801906213e-06,
            ('G', 'T', 9): 1.1680059801906213e-06,
            ('T', 'A', 0): 0.002337179966361433,
            ('T', 'A', 1): 0.0035051859465520547,
            ('T', 'A', 2): 1.1680059801906213e-06,
            ('T', 'A', 3): 0.0280333115305551,
            ('T', 'A', 4): 1.1680059801906213e-06,
            ('T', 'A', 5): 1.1680059801906213e-06,
            ('T', 'A', 6): 1.1680059801906213e-06,
            ('T', 'A', 7): 0.0035051859465520547,
            ('T', 'A', 8): 1.1680059801906213e-06,
            ('T', 'A', 9): 1.1680059801906213e-06,
            ('T', 'C', 0): 0.0035051859465520547,
            ('T', 'C', 1): 1.1680059801906213e-06,
            ('T', 'C', 2): 1.1680059801906213e-06,
            ('T', 'C', 3): 0.03270533545131759,
            ('T', 'C', 4): 1.1680059801906213e-06,
            ('T', 'C', 5): 1.1680059801906213e-06,
            ('T', 'C', 6): 1.1680059801906213e-06,
            ('T', 'C', 7): 0.0011691739861708118,
            ('T', 'C', 8): 1.1680059801906213e-06,
            ('T', 'C', 9): 1.1680059801906213e-06,
            ('T', 'G', 0): 0.0011691739861708118,
            ('T', 'G', 1): 0.0011691739861708118,
            ('T', 'G', 2): 1.1680059801906213e-06,
            ('T', 'G', 3): 0.024529293589983237,
            ('T', 'G', 4): 1.1680059801906213e-06,
            ('T', 'G', 5): 1.1680059801906213e-06,
            ('T', 'G', 6): 0.002337179966361433,
            ('T', 'G', 7): 1.1680059801906213e-06,
            ('T', 'G', 8): 1.1680059801906213e-06,
            ('T', 'G', 9): 1.1680059801906213e-06,
            ('T', 'T', 0): 1.1680059801906213e-06,
            ('T', 'T', 1): 1.1680059801906213e-06,
            ('T', 'T', 2): 0.015185245748458268,
            ('T', 'T', 3): 1.1680059801906213e-06,
            ('T', 'T', 4): 1.1680059801906213e-06,
            ('T', 'T', 5): 1.1680059801906213e-06,
            ('T', 'T', 6): 1.1680059801906213e-06,
            ('T', 'T', 7): 0.14132989160904538,
            ('T', 'T', 8): 1.1680059801906213e-06,
            ('T', 'T', 9): 0.009345215847505162,
        }
        return emissions[(seq_x[x], seq_y[y], round((precision-1)*c))]


class ClassifierAnnotationIndelState(ClassifierIndelState):
    def __init__(self, *args, **kwargs):
        ClassifierIndelState.__init__(self, *args, **kwargs)

    def _emission(self, c, seq_x, x, seq_y, y):
        emissions = {
            ('A', 0): 1.2339585389930894e-05,
            ('A', 1): 1.2339585389930894e-05,
            ('A', 2): 1.2339585389930894e-05,
            ('A', 3): 1.2339585389930894e-05,
            ('A', 4): 0.13574777887462974,
            ('A', 5): 0.06171026653504439,
            ('A', 6): 1.2339585389930894e-05,
            ('A', 7): 1.2339585389930894e-05,
            ('A', 8): 1.2339585389930894e-05,
            ('A', 9): 1.2339585389930894e-05,
            ('C', 0): 1.2339585389930894e-05,
            ('C', 1): 1.2339585389930894e-05,
            ('C', 2): 1.2339585389930894e-05,
            ('C', 3): 1.2339585389930894e-05,
            ('C', 4): 0.1974457058242842,
            ('C', 5): 0.08638943731490617,
            ('C', 6): 1.2339585389930894e-05,
            ('C', 7): 1.2339585389930894e-05,
            ('C', 8): 1.2339585389930894e-05,
            ('C', 9): 1.2339585389930894e-05,
            ('G', 0): 1.2339585389930894e-05,
            ('G', 1): 1.2339585389930894e-05,
            ('G', 2): 1.2339585389930894e-05,
            ('G', 3): 1.2339585389930894e-05,
            ('G', 4): 0.1974457058242842,
            ('G', 5): 0.07404985192497528,
            ('G', 6): 1.2339585389930894e-05,
            ('G', 7): 1.2339585389930894e-05,
            ('G', 8): 1.2339585389930894e-05,
            ('G', 9): 1.2339585389930894e-05,
            ('T', 0): 1.2339585389930894e-05,
            ('T', 1): 1.2339585389930894e-05,
            ('T', 2): 1.2339585389930894e-05,
            ('T', 3): 1.2339585389930894e-05,
            ('T', 4): 0.20978529121421507,
            ('T', 5): 0.03703109575518261,
            ('T', 6): 1.2339585389930894e-05,
            ('T', 7): 1.2339585389930894e-05,
            ('T', 8): 1.2339585389930894e-05,
            ('T', 9): 1.2339585389930894e-05,
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
