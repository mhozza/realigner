__author__ = 'michal'

import unittest
from classifier_alignment import constants
from classifier_alignment.DataPreparer import DataPreparer, IndelDataPreparer
from classifier_alignment.DataLoader import DataLoader
from alignment import Fasta


class DataPreparerTest(unittest.TestCase):
    def __init__(self, *args):
        unittest.TestCase.__init__(self, *args)
        fname = "data/test_data/sequences/alignment.fa"
        dl = DataLoader()
        _, self.seq_x, self.ann_x, self.seq_y, self.ann_y = dl.loadSequence(fname)
        self.seq_xs = Fasta.alnToSeq(self.seq_x)
        self.seq_ys = Fasta.alnToSeq(self.seq_y)

    def _prepare_pos(self, dp, x, y):
        return dp.prepare_data(self.seq_xs, x, self.ann_x, self.seq_ys, y, self.ann_y)

    def _filter_training_data(self, data):
        return [i for i, j in zip(*data) if j == 1]

    def test_prepare_data(self):
        dp = DataPreparer(constants.window_size)
        c = [-1, 0, -1, 0, 0, 0, 2, 0, 3, 0, -1, 0, -1, 0, 2, 0, 2, 0, 2, 0]
        t = self._prepare_pos(dp, 0, 0)
        self.assertEqual(t, c)

        c = [2, 0, 3, 0, 3, 0, 2, 0, 2, 0, 2, 0, 2, 0, 2, 0, 2, 0, 3, 0]
        t = self._prepare_pos(dp, 3, 2)
        self.assertEqual(t, c)

        c = [2, 0, 1, 0, 1, 0, -1, 0, -1, 0, 3, 0, 0, 0, 1, 0, 2, 0, 0, 0]
        t = self._prepare_pos(dp, 13, 6)
        self.assertEqual(t, c)

    def test_prepare_training_data(self):
        dp = DataPreparer(constants.window_size)
        t = self._filter_training_data(dp.prepare_training_data(self.seq_x, self.ann_x, self.seq_y, self.ann_y))
        self.assertIn(self._prepare_pos(dp, 0, 0), t)
        self.assertIn(self._prepare_pos(dp, 4, 2), t)
        self.assertIn(self._prepare_pos(dp, 12, 10), t)
        self.assertIn(self._prepare_pos(dp, 13, 13), t)

        self.assertNotIn(self._prepare_pos(dp, 0, 1), t)
        self.assertNotIn(self._prepare_pos(dp, 2, 2), t)
        self.assertNotIn(self._prepare_pos(dp, 2, 1), t)
        self.assertNotIn(self._prepare_pos(dp, 12, 11), t)
        self.assertNotIn(self._prepare_pos(dp, 4, 7), t)

        self.assertNotIn(self._prepare_pos(dp, 0, 0), t[1])
        self.assertNotIn(self._prepare_pos(dp, 4, 2), t[1])
        self.assertNotIn(self._prepare_pos(dp, 12, 10), t[1])
        self.assertNotIn(self._prepare_pos(dp, 13, 13), t[1])


class IndelDataPreparerTest(DataPreparerTest):
    def __init__(self, *args):
        DataPreparerTest.__init__(self, *args)

    def test_prepare_data(self):
        dp = IndelDataPreparer(0, constants.window_size)
        c = [-1, 0, -1, 0, 0, 0, 2, 0, 3, 0, -1, 0, -1, 0, 2, 0, 2, 0]
        t = self._prepare_pos(dp, 0, 0)
        self.assertEqual(t, c)

        c = [2, 0, 3, 0, 3, 0, 2, 0, 2, 0, 2, 0, 2, 0, 2, 0, 2, 0]
        t = self._prepare_pos(dp, 3, 2)
        self.assertEqual(t, c)

        c = [2, 0, 1, 0, 1, 0, -1, 0, -1, 0, 3, 0, 0, 0, 1, 0, 2, 0]
        t = self._prepare_pos(dp, 13, 6)
        self.assertEqual(t, c)

    def test_prepare_training_data(self):
        dp = IndelDataPreparer(0, constants.window_size)
        t = self._filter_training_data(dp.prepare_training_data(self.seq_x, self.ann_x, self.seq_y, self.ann_y))
        self.assertIn(self._prepare_pos(dp, 2, 2), t)

        self.assertNotIn([0, 0, 2, 0, 1, 0,  1, 0, -1, 0, 0, 0, 2, 0, 0, 0, 1, 0], t)
        self.assertNotIn([2, 0, 1, 0, 1, 0, -1, 0, -1, 0, 1, 0, 2, 0, 1, 0, -1, 0], t)

        dp2 = IndelDataPreparer(1, constants.window_size)
        t2 = self._filter_training_data(dp2.prepare_training_data(self.seq_x, self.ann_x, self.seq_y, self.ann_y))
        self.assertIn(self._prepare_pos(dp2, 13, 12), t2)


if __name__ == '__main__':
    unittest.main()
