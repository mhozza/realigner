__author__ = 'michal'

from ComparingDataPreparer import ComparingDataPreparer, ComparingIndelDataPreparer


class FullComparingDataPreparer(ComparingDataPreparer):
    def combine(self, data_x, data_y):
        return [x == y for x in data_x for y in data_y]


class FullComparingIndelDataPreparer(ComparingIndelDataPreparer):
    def combine(self, data_r, data_s):
        block_size = (len(data_r))/(self.window_size)
        data_r2 = data_r[:(self.window_size//2) * block_size]\
            + data_r[(1 + self.window_size//2) * block_size:]
        return [x == y for x in data_r2 for y in data_s]
