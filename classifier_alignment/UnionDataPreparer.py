__author__ = 'michal'

from DataPreparer import DataPreparer, IndelDataPreparer


class UnionDataPreparer(DataPreparer):
    def combine(self, data_x, data_y):
        block_size = (len(data_x))/(self.window_size)
        max_v = [2]*block_size
        max_v[0] = 4
        return [
            max_v[b]*data_x[block_size*w+b]+data_y[block_size*w+b]
            for b in range(block_size)
            for w in range(self.window_size)
        ]

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

        return self.combine(data_x, data_y)


class UnionIndelDataPreparer(IndelDataPreparer):
    def combine(self, data_r, data_s):
        block_size = (len(data_r))/(self.window_size)
        max_v = [2]*block_size
        max_v[0] = 4
        data_s2 = data_s[:(self.window_size//2) * block_size] \
            + data_s[(self.window_size//2) * block_size:(1+self.window_size//2) * block_size]\
            + data_s[(self.window_size//2) * block_size:]
        return [
            max_v[b]*data_r[block_size*w+b]+data_s2[block_size*w+b]
            for b in range(block_size)
            for w in range(self.window_size)
        ]

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

        return self.combine(data_r, data_s)
