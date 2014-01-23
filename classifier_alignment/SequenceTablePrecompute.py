__author__ = 'michal'

import sys
from classifier_alignment.PairClassifier import PairClassifier
from classifier_alignment.DataPreparer import DataPreparer


class SequenceTablePrecompute():
    def __init__(self, positon_generator, seq_x, seq_y, ann_x, ann_y):
        self.position_generator = positon_generator
        self.preparer = DataPreparer(5)
        self.classifier = PairClassifier(self.preparer)
        self.table = dict()
        self.seq_x = seq_x
        self.seq_y = seq_y
        self.ann_x = ann_x
        self.ann_y = ann_y
        self.print_status = True

    def compute(self):
        if self.print_status:
            sys.stderr.write('Computing emission table...\n')
        data = [
            (self.seq_x, x, self.ann_x, self.seq_y, y, self.ann_y)
            for x, y in self.position_generator
        ]
        out = self.classifier.multi_prepare_predict(data)
        for i, d in enumerate(self.position_generator):
            self.table[d] = out[i]
        if self.print_status:
            sys.stderr.write('Emission table computed.\n')

    def get(self, x, y):
        if (x, y) in self.table:
            return self.table[(x, y)]
        return 0
