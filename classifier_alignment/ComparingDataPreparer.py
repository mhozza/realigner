__author__ = 'michal'

import constants
from DataPreparer import DataPreparer, IndelDataPreparer


class ComparingDataPreparer(DataPreparer):
    def combine(self, data_x, data_y):
        return [x == y for x, y in zip(data_x, data_y)]

    def prepare_data(
        self,
        sequence_x,
        position_x,
        annotation_x,
        sequence_y,
        position_y,
        annotation_y,
    ):
        data_x = self._prepare_sequence(
            sequence_x, position_x, annotation_x
        )
        data_y = self._prepare_sequence(
            sequence_y, position_y, annotation_y
        )

        block_size = len(data_x)/self.window_size
        base_x = data_x[(self.window_size//2) * block_size]
        base_y = data_y[(self.window_size//2) * block_size]
        return [base_x, base_y] + self.combine(data_x, data_y)

    def get_base(self, data):
        base_x = data[0]
        base_y = data[1]
        return constants.bases_reverse[base_x], constants.bases_reverse[base_y]


class ComparingIndelDataPreparer(IndelDataPreparer):
    def combine(self, data_r, data_s):
        block_size = (len(data_r))/(self.window_size)
        data_r2 = data_r[:(self.window_size//2) * block_size] \
            + data_r[(1 + self.window_size//2) * block_size:]
        return [x == y for x, y in zip(data_r2, data_s)]

    def prepare_data(
        self,
        sequence_x,
        position_x,
        annotation_x,
        sequence_y,
        position_y,
        annotation_y,
        reference=None,
    ):
        if reference is None:
            reference = self.insert_sequence

        args = [
            (sequence_x, position_x, annotation_x),
            (sequence_y, position_y, annotation_y),
        ]
        data_r = self._prepare_sequence(*args[reference])
        data_s = self._prepare_space_sequence(*args[1-reference])

        block_size = (len(data_r))/(self.window_size)
        base = data_r[(self.window_size//2) * block_size]
        return [base] + self.combine(data_r, data_s)

    def get_base(self, data):
        base = data[0]
        return constants.bases_reverse[base]
