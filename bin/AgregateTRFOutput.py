import argparse
from collections import defaultdict
import json


def listConverter(L, *types):
    try:
        for tp, f, t in types:
            L[f:t] = [tp(x) for x in L[f:t]]
        return L
    except Exception:
        return None
        


def main(input_file, length_output, consensus_output):
    
    statLen = defaultdict(int)
    statStr = defaultdict(int)
    
    with open(input_file, 'r') as f:
        lines = (listConverter(line.strip().split(' '), (int, 0, 2)) 
                 for line in f if len(line.split(' ')) >= 15)
        for line in lines:    
            if line == None:
                continue    
            statLen[round(10 * (1 + line[1] - line[0]) / len(line[-2])) / 10.0] \
                += 1
            statStr[line[-2]] += 1
        
    with open(length_output, 'w') as f:
        json.dump(statLen, f, indent=4)
    with open(consensus_output, 'w') as f:
        json.dump(statStr, f, indent=4)
        
    
if __name__ == "__main__":    
    parser = argparse.ArgumentParser(description='Aggregate stats from TRF output.')
    parser.add_argument('input', type=str, help='Program input -- output from TRF')
    parser.add_argument('lengthOutput', type=str, help='Output file')
    parser.add_argument('consensusOutput', type=str, help='Output file')
    parsed_arg = parser.parse_args()
    main(
         parsed_arg.input,
         parsed_arg.lengthOutput,
         parsed_arg.consensusOutput
    ) 
        
