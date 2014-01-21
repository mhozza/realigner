__author__ = 'michal'

from hack.PairClassifier import PairClassifier
from hack.DataPreparer import DataPreparer


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
        #positions = [(x, y) for x, y in self.position_generator]
        positions = [p for p in self.position_generator]

        if self.print_status:
            print 'computing emission table'

        data = [
            (self.seq_x, x, self.ann_x, self.seq_y, y, self.ann_y)
            for x, y in positions
        ]

        out = self.classifier.multi_prepare_predict(data)

        if self.print_status:
            print 'prediction done'

        for i, d in enumerate(positions):
            self.table[d] = out[i]

    def get(self, x, y):
        if (x, y) in self.table:
            return self.table[(x, y)]
        return 0

if __name__ == '__main__':
    pass
