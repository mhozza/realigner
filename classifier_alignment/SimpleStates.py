__author__ = 'michal'

from hmm.PairHMM import GeneralizedPairState
from hmm.GeneralizedHMM import GeneralizedState
from collections import defaultdict


class SimpleMatchState(GeneralizedPairState):
    # def compute_emissions(self, *args):
    #     return self.compute_emissions_multi([args])

    def compute_emissions_multi(self, sequences):
        data = defaultdict(float)
        count = 0.0
        for seq in sequences:
            labels, seq_x, seq_y = seq[:3]
            for label, x, y in zip(labels, seq_x, seq_y):
                if label == 'M':
                    count += 2.0
                    data[(x, y)] += 1.0
                    data[(y, x)] += 1.0

        for x in 'ACGT':
            for y in 'ACGT':
                data[(x, y)] /= count
        return data


class SimpleIndelState(GeneralizedPairState):
    def load(self, dictionary):
        GeneralizedState.load(self, dictionary)
        newemi = defaultdict(self.mathType)
        for (key, val) in self.emissions.iteritems():
            newemi[key] = val
        self.emissions = newemi
        for d in range(len(self.durations)):
            self.durations[d] = (
                tuple(self.durations[d][0]),
                self.durations[d][1]
            )

    # def compute_emissions(self, *args):
    #     return self.compute_emissions_multi([args])

    def compute_emissions_multi(self, sequences):
        data = defaultdict(float)
        count = 0.0
        for seq in sequences:
            labels, seq_x, seq_y = seq[:3]
            for label, x, y in zip(labels, seq_x, seq_y):
                if label == 'X':
                    count += 1.0
                    data[x] += 1.0
                if label == 'Y':
                    count += 1.0
                    data[y] += 1.0
        for x in 'ACGT':
            data[x] /= count
        return data

    def emission(self, X, x, dx, Y, y, dy):
        b = X[x: x + dx]
        if b == '':
            b = Y[y: y + dy]
        return self.emissions[b]
