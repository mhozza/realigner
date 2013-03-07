import argparse
import re
import gzip
from tools.file_wrapper import Open

reverseDict = {'a': 't', 'c': 'g', 'g': 'c', 't': 'a', 'A': 'T', 'C': 'G',
                   'G': 'C', 'T': 'A'}

def reverseStrand(t):
    ret = [x if x not in reverseDict else reverseDict[x] for x in t]
    ret.reverse()
    return ''.join(ret)


def Maf2FastaGen(input_file):
    
    with Open(input_file, 'r') as inp:
        aln_count = 0
        output = []
        for line in inp:
            line = line.strip()
            if len(line) == 0:
                continue
            if line[0] not in ['a', 's']:
                continue
            if line[0] == 'a':
                #out.write("\n")
                aln_count += 1
                yield output
                output = []
                continue
            line = tuple(re.split('\s+', line))
            if len(line) != 7:
                continue
            s, src, start, size, strand, srcSize, text = line
            #if strand == '-':
            #    text = reverseStrand(text)
            output.append((src, aln_count, text))
    yield output
    

def main(input_file, output_file):
    
    with Open(output_file, 'w') as out:
        for alignment in Maf2FastaGen(input_file):
            for src, aln_count, text in alignment:
                out.write('>{0}.{1}\n{2}\n'.format(src, aln_count, text))
                
                
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert MAF to FASTA')
    parser.add_argument('input', type=str, help="Input file")
    parser.add_argument('output', type=str, help="Output file")
    parsed_arg = parser.parse_args()
    main(parsed_arg.input, parsed_arg.output)