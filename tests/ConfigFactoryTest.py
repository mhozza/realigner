import unittest
from tools.ConfigFactory import ConfigFactory, ConfigObject

class ConfigFactoryTest(unittest.TestCase):
    
    def __init__(self, *p):
        unittest.TestCase.__init__(self, *p)
                    
    
    def test_configLoadingAndSaving(self):
        input_file = "data/test_data/ConfigFactoryTestData.js"
        a = ConfigFactory()
        a.addObject(ConfigObject)
        X = a.load(input_file)
        self.assertEqual(type(X[1]), type(ConfigObject()), 
                         "objectHook does not work")
        X[1] = X[1].toJSON()
        Y = [{'1': 2, 'lol': 1.4}, 
             {'__name__': 'ConfigObject'}, 
             [1, 2, 3, 4, {'1': 2}]]
        self.assertEqual(X[0], Y[0], "loading of json does not work")
        self.assertEqual(X[2], Y[2], "loading of json does not work")
        self.assertEqual(X[1], Y[1], "saving to \"json\" is not working: " + \
                                     str(X) + " != " + str(Y))
        self.assertEqual(X, Y, "this should not happened")

    
if __name__ == '__main__':
    unittest.main()