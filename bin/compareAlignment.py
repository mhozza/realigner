import json
from alignment import Fasta
import argparse
from collections import defaultdict
from tools.file_wrapper import Open
from alignment.Alignment import Alignment
from tools import perf

@perf.runningTimeDecorator
def main():
    parser = argparse.ArgumentParser(description='Analyze alignment.')
    parser.add_argument('correct', type=str, help='Correct alignment')
    parser.add_argument('aln', type=str, help='Alignment to analyze')
    parser.add_argument('output_file', type=str, help='Output file')
    parsed_arg = parser.parse_args()
    
    separator = '[.][0-9]+$'
    
    output = []
    
    for correct, alignment in zip(
        Fasta.load(parsed_arg.correct, separator, Alignment),
        Fasta.load(parsed_arg.aln, separator, Alignment)
    ):
        cc = correct.getCoordPairs(False)
        ac = alignment.getCoordPairs(False)
        
        c = set(cc)
        a = set(ac)
        
        intersect = c.intersection(a)
        not_in_c = c.difference(a)
        not_in_a = a.difference(c)
        symm_diff = c.symmetric_difference(a)
        
        # Find long segments that are correctly aligned
        cseg = [1 if x in a else 0 for x in cc]
        seg_len = []
        length = 0
        segment_length_histogram = defaultdict(int)
        for x in cseg:
            if x == 0 and length != 0:
                segment_length_histogram[x] += 1
            length = length * x + x
            seg_len.append(length)
        if length > 0:
            segment_length_histogram[x] += 1
        
        output.append({
            'corect': parsed_arg.correct,
            'alignment': parsed_arg.aln,
            'c-lenght': len(cc),
            'a-length': len(cc),
            'intersect': len(intersect),
            'c-a': len(not_in_c),
            'a-c': len(not_in_a),
            'symmetric_difference': len(symm_diff),
            'correct_len_histogram': segment_length_histogram
        })
            
    with Open(parsed_arg.output, 'w') as f:
        json.dump(output, f, indent=4)
    

if __name__ == '__main__':
    main()
    perf.printAll() 
