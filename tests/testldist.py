from repeats.RepeatLengthDistribution import RepeatLengthDistribution
import sys
import random
from collections import defaultdict

def sampleGeom(p, start=0):
    while random.random() < p:
        start += 1
    return start

def getProb(p, n, start=0):
    return (1-p) * (p **(n - start))
    

if __name__ == '__main__':
    examples = 100000
    for p in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]:
        dist = defaultdict(int)
        for _ in range(examples):
            dist[sampleGeom(p, 2)] += 1
        
        D = RepeatLengthDistribution(start=2,fractions=[1.0])
        D.train(dist, 1, 2)
        dist2 = defaultdict(int)
        for _ in range(examples):
            dist2[D.sample()] += 1
        k = dist.keys()
        k.extend(dist2.keys())
        k = set(k)
        print p, D.p, sum([float(abs(dist[key] - dist2[key]))/examples for key in k]), \
              sum([float(abs(float(dist[key]/examples) - D[key])) for key in k]), \
              sum([abs(getProb(1-D.p, i, start=2) - D[i]) for i in k])
