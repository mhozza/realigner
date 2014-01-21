import os
print os.getcwd()

from hack.PairClassifier import PairClassifier
import itertools
from hack.DataPreparer import DataPreparer


window_size = 1


def compute_norm_constant(clf):
    def create_annotation(ann_str):
        return {
            "gene": ann_str
        }

    print('Computing normalization constant.')
    pos = min(window_size//2 + 1, window_size - 1)
    if window_size > 1:
        data = (
            (
                seq_x, pos, create_annotation(ann_x),
                seq_y, pos, create_annotation(ann_y),
            )
            for seq_x in itertools.product('ACGT', repeat=window_size)
            for seq_y in itertools.product('ACGT', repeat=window_size)
            for ann_x in itertools.product('01', repeat=window_size)
            for ann_y in itertools.product('01', repeat=window_size)
        )
    else:
        data = (
            (
                seq_x, pos, create_annotation(ann_x),
                seq_y, pos, create_annotation(ann_y),
            )
            for seq_x in 'ACGT'
            for seq_y in 'ACGT'
            for ann_x in '01'
            for ann_y in '01'
        )

    s = sum(clf.multi_prepare_predict(data))
    return s


if __name__ == '__main__':
    dp = DataPreparer(window_size)
    clf = PairClassifier(dp, filename='data/randomforest1.clf')
    print('Normalization constant:', compute_norm_constant(clf))
