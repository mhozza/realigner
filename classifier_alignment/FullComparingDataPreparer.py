__author__ = 'michal'

from ComparingDataPreparer import ComparingDataPreparer, ComparingIndelDataPreparer


class FullComparingDataPreparer(ComparingDataPreparer):
    def combine(self, data_x, data_y):
        assert(len(data_x) == len(data_y))
        block_size = (len(data_x))/(self.window_size)
        return [
            data_x[x + b] == data_y[y + b]
            for x in xrange(len(data_x)//block_size)
            for y in xrange(len(data_y)//block_size)
            for b in xrange(block_size)
        ]
        # return [x == y for x in data_x for y in data_y]


class FullComparingIndelDataPreparer(ComparingIndelDataPreparer):
    def combine(self, data_r, data_s):
        block_size = (len(data_r))/(self.window_size)
        return [
            data_r[r + b] == data_s[s + b]
            for r in xrange(len(data_r)//block_size)
            for s in xrange(len(data_s)//block_size)
            for b in xrange(block_size)
        ]
        # return [x == y for x in data_r2 for y in data_s]
