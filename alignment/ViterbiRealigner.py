import json
# from repeats.RepeatGenerator import RepeatGenerator
# from collections import defaultdict
from alignment.Realigner import Realigner
from algorithm.LogNum import LogNum
from tools.file_wrapper import Open
from tools.debug import jsonize, dejsonize_struct
from tools import perf
from classifier_alignment.AnnotationLoader import AnnotationLoader
from classifier_alignment.SequenceTablePrecompute import SequenceTablePrecompute
from classifier_alignment.ClassifierState import ClassifierState


class ViterbiRealigner(Realigner):
    def __init__(self):
        self.table = None
        return

    @perf.runningTimeDecorator
    def computeViterbiTable(self):
        if 'viterbi' not in self.io_files['input']:
            for state in self.model.states:
                if isinstance(state, ClassifierState):
                    #Fixme toto je skarede a zle!!!
                    _, ann_x, ann_y = AnnotationLoader().get_annotations(
                        "data/sequences/simulated/simulated_alignment.js"
                    )
                    emission_table = SequenceTablePrecompute(
                        state.clf, self.positionGenerator, self.X, self.Y, ann_x, ann_y
                    )
                    emission_table.compute()
                    state.set_emission_table(emission_table)

            self.table = self.model.getViterbiTable(
                self.X, 0, len(self.X),
                self.Y, 0, len(self.Y),
                positionGenerator=self.positionGenerator
            )
            x = jsonize(self.table)
            if 'viterbi' in self.io_files['output']:
                with Open(self.io_files['output']['viterbi'], 'w') as f:
                    json.dump(x, f, indent=4)
        else:
            self.table = dejsonize_struct(
                json.load(Open(self.io_files['input']['viterbi'])),
                (
                    list,
                    (
                        dict,
                        int,
                        (
                            dict,
                            (tuple, int),
                            (
                                tuple,
                                lambda x: LogNum(x, False),
                                int)))))

    @perf.runningTimeDecorator
    def prepareData(self, *data):
        data = Realigner.prepareData(self, *data)
        arguments = 0

        self.computeViterbiTable()
        return data[arguments:]

    @perf.runningTimeDecorator
    def realign(self, x, dx, y, dy):
        if 'viterbi_path' not in self.io_files['input']:
            path = self.model.getViterbiPath(self.table)
            if 'viterbi_path' in self.io_files['output']:
                with Open(self.io_files['output']['viterbi_path.js'], 'w') as f:
                    json.dump(jsonize(path), f, indent=4)
        else:
            path = dejsonize_struct(
                json.load(Open(self.io_files['input']['viterbi_path'])),
                (
                    list,
                    (
                        tuple,
                        int,
                        (tuple, int),
                        (tuple, int),
                        lambda x: LogNum(x, False))))

        X = ""
        Y = ""
        A = ""

        for (state, (_x, _y), (_dx, _dy), _) in path:
            X += self.X[_x - _dx:_x] + ('-' * (max(_dx, _dy) - _dx))
            Y += self.Y[_y - _dy:_y] + ('-' * (max(_dx, _dy) - _dy))
            A += self.model.states[state].getChar() * max(_dx, _dy)

        return [(self.X_name, X), ("viterbi annotation of " + self.X_name +
                                   " and " + self.Y_name, A),
                (self.Y_name, Y)]
