import json
import random
import math
from tools.my_rand import rand_generator
from collections import defaultdict


class RepeatLengthDistribution:
    # Mix of indel lenght distribution and arbitrary distribution
    
    def __init__(self, p=0.5, start=2, fractions=[0.5, 0.05, 0.05, 0.05, 
                                                  0.05, 0.05, 0.05, 0.05, 
                                                  0.05, 0.05]):
        self.p = p
        self.samplingConst = 0.0
        self.fractionSampler = None
        self.start = 0
        self.fractions = []
        self.setParams(p, start, fractions)
    
    
    def setParams(self, p, start, fractions):
        self.p = p
        self.samplingConst = math.log(1 - p)
        self.fractionSampler = rand_generator(
            zip(
                range(len(fractions)),
                fractions
            )
        )
        self.start = start
        self.fractions = fractions
    
        
    def sample(self):
        sz = len(self.fractions)
        baselength = math.floor(math.log(1 - random.random()) / 
                                self.samplingConst)
        return (baselength * sz + self.fractionSampler()) / sz
    
    
    #TODO: check corner cases and math
    def train(self, dist, fractionsize=10, forcesize=None):
        iterator = dist
        if type(dist) in [dict, defaultdict]:
            iterator = dist.iteritems()
        bases = defaultdict(float)
        offsets = defaultdict(float)
        if forcesize == None:
            forcesize = 0
            
        for key, value in iterator:
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
            X += k * v
        p = n / X
        self.setParams(p, start, fractions)
     
    
    def getitem(self, item):
        item -= self.start
        if item < 0:
            return 0.0
        sz = len(self.fractions)
        item = int(math.floor(item * sz))
        base = item / sz
        offset = item % sz
        return self.fractions[offset] * (self.p ** (base - 1)) * (1 - self.p)