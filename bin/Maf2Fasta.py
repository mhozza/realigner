import argparse
import re

reverseDict = {'a': 't', 'c': 'g', 'g': 'c', 't': 'a', 'A': 'T', 'C': 'G',
               'G': 'C', 'T': 'A'}
def reverseStrand(t):
    ret = [x if x not in reverseDict else reverseDict[x] for x in t]
    ret.reverse()
    return ''.join(ret)
        
aln_count = 0

parser = argparse.ArgumentParser(description='Convert MAF to FASTA')
parser.add_argument('input', type=str, help="Input file")
parser.add_argument('output', type=str, help="Output file")
parsed_arg = parser.parse_args()

with open(parsed_arg.input, 'r') as inp:
    with open(parsed_arg.output, 'w') as out: 
        for line in inp:
            line = line.strip()
            if len(line) == 0:
                continue
            if line[0] not in ['a', 's']:
                continue
            if line[0] == 'a':
                #out.write("\n")
                aln_count += 1
                continue
            line = tuple(re.split('\s+', line))
            if len(line) != 7:
                continue
            s, src, start, size, strand, srcSize, text = line
            #if strand == '-':
            #    text = reverseStrand(text)
            out.write('>{0}.{1}\n{2}\n'.format(src, aln_count, text))