import unittest
from MemoryPatterns import every, first, last, sqrt

class ConfigFactoryTest(unittest.TestCase):
    
    def test_every(self): 
        tests = [
            (0, []),
            (1, [True]),
            (10, [True, True, True, True, True, True, True, True, True, True])
        ]
        for (x, Y) in tests:
            X = list(every(x))
            self.assertEqual(X, Y, "MemoryPattern.every(" + str(x) + \
                             ") does not work: " + str(X) + " != " + str(Y))              
    
        
    def test_last(self):
        tests = [
            (0, 0, []),
            (1, 1, [True]),
            (2, 1, [False, True]),
            (5, 3, [False, False, True, True, True]),
            (10, 2, [False, False, False, False, False, False, False, False, 
                     True, True])
        ]
        for (x, k, Y) in tests:
            X = list(last(x, k))
            self.assertEqual(X, Y, "MemoryPattern.last(" + str(x) + ", " + \
                             str(k) + ") does not work: " + str(X) + " != " + \
                             str(Y))   
    
    
    def test_first(self):  
        tests = [
            (0, 0, []),
            (1, 1, [True]),
            (2, 1, [True, False]),
            (5, 3, [True, True, True, False, False]),
            (10, 2, [True, True, False, False, False, False, False, False, 
                     False, False])
        ]
        for (x, k, Y) in tests:
            X = list(first(x, k))
            self.assertEqual(X, Y, "MemoryPattern.first(" + str(x) + ", " + \
                             str(k) + ") does not work: " + str(X) + " != " + \
                             str(Y))     
    
    
    def test_sqrt(self):
        tests = [
            (0, []),
            (1, [True]),
            (2, [True, True]),
            (3, [True, True, True]),
            (4, [True, False, True, True]),
            (5, [True, False, True, False, True]),
            (8, [True, False, True, False, True, False, True, True]),
            (15, [True, False, False, True, False, False, True, False, False, 
                  True, False, False, True, False, True]),
        ]
        for (x, Y) in tests:
            X = list(sqrt(x))
            self.assertEqual(X, Y, "MemoryPattern.sqrt("+ str(x) + \
                                   ") does not work: " + str(X) + " != " + \
                                   str(Y))

    
if __name__ == '__main__':
    unittest.main()