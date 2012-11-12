import unittest
from Graphs import toposort, orderToDict

class AlignmentIteratorTest(unittest.TestCase):
    
    def __init__(self, *p):
        unittest.TestCase.__init__(self, *p)
        self.G = dict()

    def setUp(self):
        self.G = {
            0: {3: 1},
            1: {2: 1,
                5: 1},
            2: {3: 1},
            4: {3: 1,
                5: 1},
            5: {9: 1},
            6: {5: 1,
                14: 1},
            7: {10: 1},
            8: {13: 1},
            9: {10: 1},
            10: {6: 1},
            12: {13: 1,
                 11: 1},
            13: {14: 1},
            14: {8: 1}}                
    
    def test_toposort(self):
        X = toposort(self.G)
        Y = [3, 0, 2, 13, 8, 14, 6, 10, 9, 5, 1, 4, 7, 11, 12]
        self.assertEqual(X, Y, "Topological sort is not working: " + \
                               str(X) + " != " + str(Y))
    
    
    def test_tupleList(self):
        X = orderToDict([3, 2, 1, 0])
        Y = {0: 3, 1: 2, 2: 1, 3: 0}
        self.assertEqual(X, Y, "orderToDict is not working: " + \
                               str(X) + " != " + str(Y))

    
if __name__ == '__main__':
    unittest.main()