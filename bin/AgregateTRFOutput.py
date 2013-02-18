import argparse
from collections import defaultdict
import json
 
parser = argparse.ArgumentParser(description='Agregate output from TRF alignment.')
parser.add_argument('input', type=str, help='Program input -- output from TRF')
parser.add_argument('lengthOutput', type=str, help='Output file')
parser.add_argument('consensusOutput', type=str, help='Output file')
parsed_arg = parser.parse_args()

def listConverter(L, *types):
    for tp, f, t in types:
        L[f:t] = [tp(x) for x in L[f:t]]
    return L

statLen = defaultdict(int)
statStr = defaultdict(int)

with open(parsed_arg.input, 'r') as f:
    lines = (listConverter(line.strip().split(' '), (int, 0, 2)) 
             for line in f if len(line.split(' ')) >= 15)
    for line in lines:        
        statLen[1 + line[1] - line[0]] += 1
        statStr[line[-2]] += 1
    
with open(parsed_arg.lengthOutput, 'w') as f:
    json.dump(statLen, f, indent=4)
with open(parsed_arg.consensusOutput, 'w') as f:
    json.dump(statStr, f, indent=4)
    
        
        
        
