import random
import math
from tools.my_rand import rand_generator
from collections import defaultdict
from tools.ConfigFactory import ConfigObject
from tools.Exceptions import ParseException


class RepeatLengthDistribution(ConfigObject):
    # Mix of indel lenght distribution and arbitrary distribution
    
    def __init__(self, mathType=float, p=0.5, start=0, 
                 fractions=[0.5, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 
                            0.05, 0.05]):
        self.mathType=mathType
        self.p = self.mathType(p)
        self.samplingConst = self.mathType(0.0)
        self.fractionSampler = None
        self.start = self.mathType(0)
        self.fractions = []
        self.setParams(p, start, fractions)
    
    
    def load(self, dictionary):
        ConfigObject.load(self, dictionary)
        #Detect if user provides the data or not
        start = 0
        if 'start' in dictionary:
            start = float(dictionary['start'])
        if 'data' not in dictionary:
            if 'p' not in dictionary:
                raise ParseException(
                    'Probability is missing in RepeatLengthDistribution'
                )
            p = float(dictionary['p'])
            if 'fractions' not in dictionary:
                raise ParseException(
                    'Fractions are missing in RepeatLengthDistribution'
                )
            fractions = dictionary['fractions']
            self.setParams(p, start, fractions)
        else:
            data = dictionary['data']
            if 'fractionssize' not in dictionary:
                raise ParseException(
                    'Number of fractions is missing in RepeatLengthDistribution'
                )
            self.train(data, int(dictionary['fractionssize']), start)


    def toJSON(self):
        ret = ConfigObject.toJSON(self)
        ret['p'] = self.p
        ret['start'] = self.start
        ret['fractions'] = self.fractions
        return ret         


    def setParams(self, p, start, fractions):
        self.p = self.mathType(p)
        self.samplingConst = math.log(1.0 - p)
        fractions = [self.mathType(x) for x in fractions]
        self.fractionSampler = rand_generator(
            zip(
                fractions,
                range(len(fractions)), 
            ),
            normalize=True
        )
        self.start = start
        self.fractions = fractions
    
        
    def sample(self):
        sz = len(self.fractions)
        baselength = math.floor(math.log(1 - random.random()) / 
                                self.samplingConst)
        return (baselength * sz + self.fractionSampler()) / sz + self.start
    
    
    def train(self, dist, fractionsize=10, forcesize=None):
        iterator = dist
        if type(dist) in [dict, defaultdict]:
            iterator = dist.iteritems()
        bases = defaultdict(float)
        offsets = defaultdict(float)
        if forcesize == None:
            forcesize = 0
            
        for key, value in iterator:
            key = float(key)
            value = float(value)
            k = int(math.floor((key - forcesize) * fractionsize))
            if k < 0: 
                continue
            base = k / fractionsize
            offset = k % fractionsize
            bases[base] += value
            offsets[offset] += value
        fractions = [offsets[k] for k in range(fractionsize)]
        total = sum(fractions)
        fractions = [float(x) / total for x in fractions]
        n = 0.0
        X = 0.0
        for k, v in bases.iteritems():
            n += v
            X += (k + 1) * v
        p = n / X
        if p >= 1: 
            p = 1.0 - 10e-12
        self.setParams(p, forcesize, fractions)
        
    
    def getParams(self):
        return (self.p, self.start, self.fractions)
     
    
    def __getitem__(self, item):
         
        item -= self.start
        if item < 0:
            return self.mathType(0.0)
        sz = len(self.fractions)
        item = int(math.floor(item * sz))
        base = item / sz
        offset = item % sz
        return self.fractions[offset] * self.p * \
            ((self.mathType(1) - self.p) ** (base))
    
if __name__ == '__main__':
    D = RepeatLengthDistribution(0.99999, 5, [0.74, 0.23, 0.02, 0.01])
    X = [(D.sample(), 1) for _ in range(100000)]
    nD = RepeatLengthDistribution()
    nD.train(X, 4, 5)
    print nD.getParams()
    
