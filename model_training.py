#!/usr/bin/python
__author__ = 'michal'
from classifier_alignment.DataLoader import DataLoader
from hmm.HMMLoader import HMMLoader
import json
import argparse
from collections import defaultdict
from classifier_alignment.ClassifierState import register as register_classifier_states
from classifier_alignment.ClassifierAnnotationState import register as register_annotation_states


class ModelTraining:
    def __init__(self):
        self.position_independent = False
        self.model = None
        self.model_states = ['M', 'X']
        self.states_dict = dict()
        self.fname = None

    def load_model(self, fname):
        loader = HMMLoader(float)
        register_classifier_states(loader)
        register_annotation_states(loader)

        self.fname = fname
        self.model = loader.load(fname)
        self.states_dict = dict()
        for i, state in enumerate(self.model['model'].states):
            self.states_dict[state.onechar] = i

    def save_model(self):
        self.save_model_as(self.fname)

    def save_model_as(self, fname):
        model_json = dict()
        for k in self.model:
            if k == 'model':
                model_json[k] = self.model[k].toJSON()
            else:
                model_json[k] = self.model[k]
        with open(fname, 'w') as f:
            json.dump(model_json, f)

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
        return self.transitions_multi([labels])

    def transitions_multi(self, labels_list):
        counts = defaultdict(lambda: defaultdict(float))
        for labels in labels_list:
            for i, state in enumerate(labels):
                if state == '-':
                    continue
                j = i + 1
                while j < len(labels) and labels[j] == '-':
                    j += 1
                if i < j < len(labels):
                    nextstate = labels[j]
                    counts[state][nextstate] += 1

        sums = dict()
        for state in 'MXY':
            s = sum(counts[state].values())
            sums[state] = s
        return {
            '{}{}'.format(k, k2): v2 for k, v in counts.iteritems() for k2, v2 in v.iteritems()
        }, sums

    def emissions(self, labels, seq_x, seq_y, a_x, a_y):
        return self.emissions_multi([(labels, seq_x, seq_y, a_x, a_y)])

    def emissions_multi(self, sequences):
        data = dict()
        try:
            for onechar in self.model_states:
                state = self.model['model'].states[self.states_dict[onechar]]
                data[onechar] = state.compute_emissions_multi(sequences)
            return data
        except AttributeError:
            # print 'compute_emissions not suppoorted by model!'
            return None

    def make_position_independent(self):
        pass

    def train_single(self, s_x, s_y, a_x, a_y):
        labels = list(self.labels(s_x, s_y))
        return self.transitions(labels), self.emissions(labels, s_x, s_y, a_x, a_y)

    def train_multi(self, sequences):
        labels = [list(self.labels(s[1], s[3])) for s in sequences]
        labeled_sequences = [
            [l, s_x, s_y, a_x, a_y]
            for l, (_, s_x, a_x, s_y, a_y) in zip(labels, sequences)
        ]
        transitions = self.transitions_multi(labels)
        emissions = self.emissions_multi(labeled_sequences)
        return transitions, emissions

    def train(self, dirname):
        def summarize_transitions(transitions):
            def get_prob(t, key):
                if key in t[0]:
                    return t[0][key]
                else:
                    return 0

            res = dict()
            for state in 'MXY':
                s = float(sum((t[1][state] for t in transitions)))
                for state2 in 'MXY':
                    res[state+state2] = sum((get_prob(t, state+state2) for t in transitions))/s
            return res

        def summarize_emissions(emissions):
            if not emissions:
                return {}
            res = dict()
            keys = emissions[0][0].keys()
            count = float(sum((e[1] for e in emissions)))
            for k in keys:
                res[k] = sum((e[1] * e[0][k] for e in emissions)) / count
            return res

        dl = DataLoader()
        sequences = dl.loadDirectory(dirname)
        transitions = list()
        emissions_m = list()
        emissions_x = list()
        for _, s_x, a_x, s_y, a_y in sequences:
            t, e = self.train_single(s_x, s_y, a_x, a_y)
            transitions.append(t)
            if e is not None:
                emissions_m.append(e['M'])
                emissions_x.append(e['X'])

        return summarize_transitions(transitions), {
            'M': summarize_emissions(emissions_m), 'X': summarize_emissions(emissions_x)
        }

    def set_model_emissions(self, emissions):
        for state in self.model['model'].states:
            ch = state.onechar
            if ch == 'Y':
                ch = 'X'
            state.emissions = emissions[ch]

    def set_model_transitions(self, transitions):
        model = self.model['model']
        model.clearTransitions()
        for transition, probability in transitions.iteritems():
            model.addTransition(
                self.states_dict[transition[0]],
                self.states_dict[transition[1]],
                probability,
            )

    def train_model(self, fname, data_dirname):
        self.load_model(fname)
        transitions, emissions = self.train(data_dirname)
        self.set_model_transitions(transitions)
        self.set_model_emissions(emissions)
        self.save_model()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'model', metavar='model', type=str, nargs='?', default='data/models/SimpleHMM2.js'
    )
    parser.add_argument(
        'dir', metavar='data dir', type=str, nargs='?', default='data/model_train_seq/bio'
    )
    args = parser.parse_args()
    training = ModelTraining()
    training.train_model(args.model, args.dir)
