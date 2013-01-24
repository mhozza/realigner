"""
Unittests for AlignmentIterator module
"""
from alignment.AlignmentIterator import AlignmentPositionGenerator, \
                                        AlignmentBeamGenerator, \
                                        AlignmentFullGenerator, \
                                        seq_len
import unittest

class AlignmentIteratorTest(unittest.TestCase):
    
    def setUp(self):
        self.Alignment = (
            "ACG--C-A--CA-C",
            "AC-TGGGAC-CACC")
        return
    
            
    def test_positions(self):
        X = [(0, 0), (1, 1), (2, 1), (2, 2), (2, 3), (3, 4), (3, 5), (4, 6),
             (4, 7), (4, 7), (5, 8), (6, 9), (6, 10), (7, 11)]
        Y = list(AlignmentPositionGenerator(self.Alignment))
        self.assertEqual(X, Y, "Position generator does not work: " + 
                         str(X) + " != " + str(Y))
    
    
    def test_beam(self):
        self.assertEqual(self.Alignment, (
            "ACG--C-A--CA-C",
            "AC-TGGGAC-CACC"))
        maxX = seq_len(self.Alignment[0])
        maxY = seq_len(self.Alignment[1])
        for width in range(0, 20):
            positions = AlignmentPositionGenerator(self.Alignment)
            X = set()
            for x in positions:
                for i in range(-width, width+1):
                    for j in range(-width, width+1):
                        if x[0] + i < 0 or \
                           x[1] + j < 0 or \
                           x[0] + i >= maxX or \
                           x[1] + j >= maxY:
                            continue
                        X.add((x[0] + i, x[1] + j))
            Y = set(AlignmentBeamGenerator(self.Alignment, width))
            self.assertEqual(X, Y, "Beam iterator is not correct:\n\t{0} !=\n\t{1}".
                             format(X, Y))
     
            
    def test_full(self):
       alignment = ("ACTA---", "TCTCTCT")
       X = list(AlignmentFullGenerator(alignment))
       Y = list(((i, j)for i in range(4) for j in range(7)))
       self.assertEqual(X,
                        Y,
                        "Full iterator is not correct: " + str(X) + \
                        " != " + str(Y))
    
    
if __name__ == '__main__':
    unittest.main()
