__author__ = 'michal'

from hmm.PairHMM import GeneralizedPairState
from collections import defaultdict

class SimpleMatchState(GeneralizedPairState):
    def compute_emmisions(self, labels, seq_x, seq_y):
        data = defaultdict(float)
        for label, x, y in zip(labels, seq_x, seq_y):
            if label == 'M':
                data[(x, y)] += 1
        for x in 'ACGT':
            for y in 'ACGT':
                data[(x, y)] /= float(len(data))
        return data


class SimpleIndelState(GeneralizedPairState):
    def compute_emmisions(self, labels, seq_x):
        data = defaultdict(float)
        for label, x, y in zip(labels, seq_x, seq_y):
            if label != 'M':
                if x != '-':
                    data[x] += 1
                if y != '-':
                    data[y] += 1
        for x in 'ACGT':
            data[x] /= float(len(data))
        return data

