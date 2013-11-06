import re
import sys
import os
import math
from collections import defaultdict, OrderedDict

# TODO: Rychlejsie porovnavanie error, ziskavanie patternov z chyb
# TODO: Vypis subory v ktorych je chyba
# TODO: Vyber si ktore joby (cez id alebo nazov) chces zobrazovat)

def colored(string, color):
    CSI = "\x1B["
    #reset = CSI+"m"
    d = {'red': '31;1m', 'black': '30m', 'yellow': '33m', 'green': '32;1m'}
    return CSI + d[color] + string + CSI + "0m"


def get_files(path):
    for fl in os.listdir(path):
        f = path + '/' + fl
        if os.path.isfile(f):
            yield f


def get_error_logs(path):
    error_re = re.compile('e[0-9]+$')
    int_re = re.compile('[0-9]+$')
    for filename in get_files(path):
        splitted = filename.split('.')
        if len(splitted) == 1:
            continue
        array = None
        job_id = None
        job_name = None
        if len(splitted) == 2:
            l = splitted[-1]
            if not error_re.match(l):
                continue
            job_id = int(l[1:])
            job_name = splitted[0]
        elif len(splitted) > 2:
            l = splitted[-1]
            p = splitted[-2]
            job_name = '.'.join(splitted[:-2])
            if not error_re.match(l) and not error_re.match(p):
                continue
            if error_re.match(l):
                job_id = int(l[1:])
                job_name += '.' + p
            else:
                if not int_re.match(l):
                    continue
                array = int(l)
                job_id = int(p[1:])
        yield job_name, job_id, array, filename            


def parse_error_log(filename):
    perf = OrderedDict()
    perf_re = re.compile('(.*) ([0-9.e-]+) seconds\.$')
    error = None
    with open(filename, 'r') as f:
        logfile = list(f)
    good_count = 0
    for line in logfile:
        r = perf_re.match(line.strip('\n'))
        if r == None:
            if len(line.strip()) == 0:
                good_count += 1
            continue
        good_count += 1
        perf[r.group(1)] = float(r.group(2))
    if len(logfile) != good_count:
        error = ''.join(logfile)
    return perf, error        


def dist(s1, s2):
    if s1 == s2: 
        return 0.0
    d = [i for i in range(len(s2) + 1)]
    for i in range(len(s1)):
        nd = [0 for _ in range(len(s2) + 1)]
        nd[0] = d[0] + 1
        for j in range(1, len(s2) + 1):
            nd[j] = min([
                d[j] + 1,
                nd[j - 1] + 1,
                d[j - 1] + (1 if s1[i] == s2[j - 1] else 0)
            ])
        d = nd
    
    return float(d[-1]) * (s1.count('\n') + s2.count('\n')) / (len(s1) + len(s2))


def split_data(k):
    if len(k) == 0:
        return None, k
    if k[0] not in ['|', '+']:
        return None, k
    a, b = tuple(k.split('+', 1))
    return a + '+', b



class PerfAggregator:
    
    def __init__(self):
        self.data = OrderedDict()
        self.prefix = defaultdict(str)
    
    def addDataPoint(self, d):
        for k, v in d.iteritems():
            prefix, sufix = split_data(k)
            if sufix not in self.data:
                self.data[sufix] = list()
            self.data[sufix].append(v)
            if prefix != None:
                self.prefix[sufix] = prefix
            
    def output(self):
        for k, v in self.data.iteritems():
            if len(v) == 0:
                print(k + ' [No data points]')
            else:
                total = sum(v)
                mean = total / len(v)
                variance = sum([(mean - x)**2 for x in v]) / len(v)
                print('{}{} {:.3} seconds [Deviation: {:.3}, {} data points].'.format(
                    self.prefix[k], k, mean, math.sqrt(variance), len(v)
                )) 
      
        
class ErrorAggregator:
    
    def __init__(self):
        self.centers = defaultdict(int)
        self.examples = defaultdict(list)
        
    def addDataPoint(self, e, filename):
        if e == None:
            return
        if len(e.strip()) == 0:
            return
        if len(self.centers) == 0:
            self.centers[e] += 1
            return
        for k, _ in self.centers.iteritems():
            d = dist('\n'.join(e.split('\n')[-3:]), '\n'.join(k.split('\n')[-3:]))
            #print 'dist', d, len(self.centers)
            if d < 0.15:
                self.centers[k] += 1
                self.examples[k].append(filename)
                return
        self.centers[e] += 1     
        
    def output(self):
        lst = list(self.centers.iteritems())
        lst.sort(key=lambda x: x[1])
        for error, count in lst:
            d = defaultdict(list)
            for x in self.examples[error][:10]:
                v = x.split('.')[-1];
                k = '.'.join(x.split('.')[:-1])
                d[k].append(v)
            out = ['{base}.{{{value}}}'.format(base=k, value = ','.join(v)) for k, v in d.iteritems()]
            print(colored('Error examples: {}\nThis error occured {} times:\n'.format(' '.join(out), count),
                          'red') + error)


jobs = defaultdict(list)
for job_name, job_id, array, filename in get_error_logs(sys.argv[1]):
    jobs[job_id, job_name].append((array, filename))
jobs = list(jobs.iteritems())
jobs.sort(key=lambda x:x[0][0])

names = defaultdict(list)
for (job_id, job_name), _ in jobs:
    names[job_name].append(job_id)
for k in names:
    names[k] = max(names[k])

jobs = [x for x in jobs if names[x[0][1]] == x[0][0]]

aggregated_data = list()
for (job_id, job_name), data in jobs:
    perf = PerfAggregator() 
    error = ErrorAggregator()
    for _, filename in data:
        p, e = parse_error_log(filename)
        perf.addDataPoint(p)
        error.addDataPoint(e, filename)
    print("""
===============================================================================
""" + colored("""Job: {} ({})""".format(job_name.split('/')[-1], job_id),
              'green'))
    perf.output()
    error.output()
