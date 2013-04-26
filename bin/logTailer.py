import re
import sys
import os
import math
from collections import defaultdict

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
    perf = defaultdict(float)
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
    return float(d[-1]) / max(len(s1), len(s2))


class PerfAggregator:
    
    def __init__(self):
        self.data = defaultdict(list)
    
    def addDataPoint(self, d):
        for k, v in d.iteritems():
            self.data[k].append(v)
            
    def output(self):
        for k, v in self.data.iteritems():
            if len(v) == 0:
                print(k + ' [No data points]')
            else:
                total = sum(v)
                mean = total / len(v)
                variance = sum([(mean - x)**2 for x in v]) / len(v)
                print('{} {} seconds [Deviation: {}, {} data points].'.format(
                    k, mean, math.sqrt(variance), len(v)
                )) 
      
        
class ErrorAggregator:
    
    def __init__(self):
        self.centers = defaultdict(int)
        
    def addDataPoint(self, e):
        if e == None:
            return
        if len(e.strip()) == 0:
            return
        if len(self.centers) == 0:
            self.centers[e] += 1
            return
        least = None
        least_ind = None
        
        for k, _ in self.centers.iteritems():
            d = dist(e, k)
            if least == None or least > d:
                least = d
                least_ind = k
        if least < 0.2:
            self.centers[least_ind] += 1
            return
        self.centers[e] += 1     
        
    def output(self):
        lst = list(self.centers.iteritems())
        lst.sort(key=lambda x: x[1])
        for error, count in lst:
            print(colored('This error occured {} times:\n'.format(count),
                          'red') + error)


jobs = defaultdict(list)
for job_name, job_id, array, filename in get_error_logs(sys.argv[1]):
    jobs[job_id, job_name].append((array, filename))
jobs = list(jobs.iteritems())
jobs.sort(key=lambda x:x[0][0])

aggregated_data = list()
for (job_id, job_name), data in jobs:
    perf = PerfAggregator() 
    error = ErrorAggregator()
    for _, filename in data:
        p, e = parse_error_log(filename)
        perf.addDataPoint(p)
        error.addDataPoint(e)
    print("""
===============================================================================
""" + colored("""Job: {} ({})""".format(job_name.split('/')[-1], job_id),
              'green'))
    perf.output()
    error.output()