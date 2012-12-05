import unittest
from algorithm.LogNum import LogNum
import operator


def toLogNum(L):
    return [LogNum(f) for f in L]
    

class ConfigFactoryTest(unittest.TestCase):
    
    def test_conversion_to_float(self):
        tests = [0.0, 1.0, 0.2, 0.3, 0.8, 0.4]
        for Y in tests:
            X = float(LogNum(Y))
            self.assertAlmostEqual(X, Y, delta=1e-7, 
                                   msg="LogNum.__float__(NumLog(" + \
                                   str() + ")) does not work: " + str(X) + \
                                   " != " + str(Y))
    
    def skelet(self, function, name, zero=True, start=0.0):
        tests = [
            [],
            [1.0],
            [1.01],
            [0.99],
            [0.95],
            [1.05],
            [1.0, 0.3, 0.1, 1.0],
            [0.1, 0.4, 0.2, 0.3, 0.9, 0.5, 0.7, 0.6, 0.8],
            [0.8, 0.3],
            [0.1, 0.1]
        ]
        if zero:
            tests.extend([
                [0.0, 0.2, 0.3, 0.8, 1.8],
                [0.2, 0.0]
            ])
        for x in tests:
            X = reduce(function, toLogNum(x), LogNum(start))
            Y = reduce(function, x, start)
            self.assertAlmostEqual(float(X), Y, delta=1e-7, msg=name + \
                                   " does not work: " + str(X) + " != " + \
                                   str(Y))
            
    
    def test_add(self):
        self.skelet(operator.add, "LogNum.__add__")
        
    
    def test_sub(self):
        self.skelet(operator.sub, "LogNum.__sub__", start=10.0)


    def test_mul(self):
        self.skelet(operator.mul, "LogNum.__mul__", start=1.0)


    def test_div(self):
        self.skelet(operator.div, "LogNum.__div__", zero=False, start=10.0)  
    
    
    def test_pow(self):
        self.skelet(operator.pow, "LogNum.__pow__", start=2.0)
    
    
    def test_lt(self):
        self.skelet(operator.lt, "LogNum.__lt__", start=1.0)          
        
            
    def test_le(self):
        self.skelet(operator.le, "LogNum.__le__", start=1.0)
        
        
    def test_eq(self):
        self.skelet(operator.eq, "LogNum.__eq__", start=1.0)
        
    
    def test_ne(self):
        self.skelet(operator.ne, "LogNum.__ne__", start=1.0)   
        
        
    def test_gt(self):
        self.skelet(operator.gt, "LogNum.__gt__", start=1.0)
        
        
    def test_ge(self):
        self.skelet(operator.ge, "LogNum.__ge__", start=1.0)
        
        
    def test_str(self):
        tests = [0.1111, 0.23, 0.47, 0.1, 0.0, 0.1, 1.0/3.0]
        for x in tests:
            X = str(LogNum(x))
            Y = str(x)
            self.assertEqual(X, Y, "LogNum.__str__ does not work: " + str(X) + \
                             " != " + str(Y))
    
    
if __name__ == '__main__':
    unittest.main()