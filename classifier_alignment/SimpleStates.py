__author__ = 'michal'

from hmm.PairHMM import GeneralizedPairState
from collections import defaultdict

class SimpleMatchState(GeneralizedPairState):
    def compute_emissions(self, labels, seq_x, seq_y, *args):
        data = defaultdict(float)
        count = 0.0
        for label, x, y in zip(labels, seq_x, seq_y):
            if label == 'M':
                count += 1
                data[(x, y)] += 1
        for x in 'ACGT':
            for y in 'ACGT':
                data[(x, y)] /= count
        return data


class SimpleIndelState(GeneralizedPairState):
    def compute_emissions(self, labels, seq_x, seq_y, *args):
        data = defaultdict(float)
        count = 0.0
        for label, x, y in zip(labels, seq_x, seq_y):
            if label != 'M':
                count += 1
                if x != '-':
                    data[x] += 1
                if y != '-':
                    data[y] += 1
        for x in 'ACGT':
            data[x] /= count
        return data

