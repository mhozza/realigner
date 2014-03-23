#!/usr/bin/python
__author__ = 'michal'
from classifier_alignment.DataLoader import DataLoader
from classifier_alignment.ClassifierAnnotationState import ClassifierAnnotationState, ClassifierAnnotationIndelState
from classifier_alignment.SimpleStates import SimpleMatchState, SimpleIndelState
from tools.utils import dict_avg as avg


class ModelTraining:
    def __init__(self):
        self.position_independent = False
        # self.model_states = [('M', ClassifierAnnotationState()), ('X', ClassifierAnnotationIndelState())]
        self.model_states = [('M', SimpleMatchState()), ('X', SimpleIndelState())]

    def load_model(self):
        pass

    def save_model(self):
        pass

    def labels(self, seq_x, seq_y):
        def state(i):
            if seq_x[i] == '-':
                if seq_y[i] == '-':
                    return '-'
                return 'Y'
            if seq_y[i] == '-':
                return 'X'
            return 'M'
        if len(seq_x) != len(seq_y):
            return
        return (state(i) for i in xrange(len(seq_x)))

    def transitions(self, labels):
            counts = dict()
            for state in 'MXY':
                counts[state] = dict()
                for nextstate in 'MXY':
                    counts[state][nextstate] = 0

            for i, state in enumerate(labels):
                if state == '-':
                    continue
                j = i + 1
                while j < len(labels) and labels[j] == '-':
                    j += 1
                if i < j < len(labels):
                    nextstate = labels[j]
                    counts[state][nextstate] += 1

            for state in 'MXY':
                s = float(sum(counts[state].values()))
                for nextstate in 'MXY':
                    if s > 0:
                        counts[state][nextstate] /= s

            return {
                k+k2: v2 for k, v in counts.iteritems() for k2, v2 in v.iteritems()
            }

    def emissions(self, seq_x, seq_y, a_x, a_y, labels):
        data = dict()
        try:
            for onechar, state in self.model_states:
                data[onechar] = state.compute_emissions(labels, seq_x, seq_y, a_x, a_y)
            return data
        except AttributeError as e:
            print 'Emissions not suppoorted by model!', e
            return None

    def start_states(self):
        return [1/3.0]*3

    def make_position_independent(self):
        pass

    def train_single(self, s_x, s_y, a_x, a_y):
        labels = list(self.labels(s_x, s_y))
        return self.transitions(labels), self.emissions(s_x, s_y, a_x, a_y, labels)

    def train(self, dirname):
        dl = DataLoader()
        sequences = dl.loadDirectory(dirname)
        start_states = self.start_states()
        transitions = list()
        emissions = list()
        for _, s_x, a_x, s_y, a_y in sequences:
            t, e = self.train_single(s_x, s_y, a_x, a_y)
            transitions.append(t)
            emissions.append(e)
        return start_states, avg(transitions), avg(emissions)

if __name__ == "__main__":
    dirname = 'data/model_train_seq/bio_test'
    training = ModelTraining()
    probabilities = training.train(dirname)
    print(probabilities)
