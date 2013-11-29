import argparse
import re
import gzip
from tools.file_wrapper import Open
from tools import perf

reverseDict = {'a': 't', 'c': 'g', 'g': 'c', 't': 'a', 'A': 'T', 'C': 'G',
                   'G': 'C', 'T': 'A'}

def reverseStrand(t):
    ret = [x if x not in reverseDict else reverseDict[x] for x in t]
    ret.reverse()
    return ''.join(ret)

def matched(expr, name):
    if len(expr) == 0:
        return True
    for ex in expr:
        if ex.search(name):
            return True
    return False

def Maf2FastaGen(input_file, sequences):
    regs = map(re.compile, sequences)

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
                if len(output) > 0 and (len(regs) == 0 or (len(output) == len(regs))):
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
            if matched(regs, src): 
                output.append((src, aln_count, text, [start, size, strand, srcSize]))
    if len(output) > 0 and (len(regs) == 0 or (len(output) == len(regs))):
        yield output
    

@perf.runningTimeDecorator
def main(input_file, output_file, sequences, output_type):
    
    with Open(output_file, 'w') as out:
        for alignment in Maf2FastaGen(input_file, sequences):
            for src, aln_count, text, rest in alignment:
                if output_type=="normal": 
                    out.write('>{0}.{1}\n{2}\n'.format(src, aln_count, text))
                elif output_type=="params":
                    out.write('>{0}.{1} {2}\n'.format(src, aln_count, ' '.join(rest)))
                
                
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert MAF to FASTA')
    parser.add_argument('input', type=str, help="Input file")
    parser.add_argument('output', type=str, help="Output file")
    parser.add_argument('--output_type', default="normal", type=str)
    parser.sequences('--sequences', nargs='*', default=[], help="Regexps for sequence selections")
    parsed_arg = parser.parse_args()
    main(parsed_arg.input, parsed_arg.output, parsed_arg.sequences, parsed_arg.output_type)
    perf.printAll()
