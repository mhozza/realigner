__author__ = 'michal'

from DataPreparer import DataPreparer, IndelDataPreparer


class CombinedDataPreparer(DataPreparer):
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

        return data_x\
            + data_y\
            + self.combine(data_x, data_y)


class CombinedIndelDataPreparer(IndelDataPreparer):
    def combine(self, data_r, data_s):
        block_size = (len(data_r))/(self.window_size)
        # data_r2 = data_r[:(self.window_size//2) * block_size] \
        #     + data_r[(1 + self.window_size//2) * block_size:]
        data_s2 = data_s[:(self.window_size//2) * block_size] \
            + data_s[(self.window_size//2) * block_size:(1+self.window_size//2) * block_size]\
            + data_s[(self.window_size//2) * block_size:]
        # return [x == y for x, y in zip(data_r2, data_s)]
        return [x == y for x, y in zip(data_r, data_s2)]

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

        return data_r\
            + data_s\
            + self.combine(data_r, data_s)
