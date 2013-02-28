import json
import os
import argparse
from bin.Maf2Fasta import Maf2FastaGen
import re

def main(alignment, working_directory, split_count, output_file, 
         seq_selectors):
    
    seq_selectors = map(re.compile, seq_selectors)
    # TODO: check na to, ci to uz existuje, a ked ano, tak to nespravil znova
    
    if not os.path.exists(working_directory):
        os.makedirs(working_directory)
    # Prepare alignment into right format
    
    filename = os.path.basename(alignment)
    extension = filename.split('.')[-1].lower()
    base = filename.split('.')[-2]
    if extension == 'fa':
        # fasta_generator = alignment
        assert(False)
    elif extension == 'maf':
        fasta_generator = Maf2FastaGen(alignment)
    else:
        assert(False)
    
    parallel_dir = '{dir}/{base}_parallel'.format(
        dir=working_directory,
        base=base,
    )
    
    if not os.path.exists(parallel_dir):
        os.makedirs(parallel_dir)
    
    filenames = ['{dir}/alignment_{index:04d}.fa'.format(dir=parallel_dir, 
                                                         index=i)
                 for i in range(split_count)]
    files = [open(name, 'w') for name in filenames] 
    
    for aln in fasta_generator:
        new_aln = []
        for src, aln_count, text in aln:
            add = False
            for selector in seq_selectors:
                if selector.match(src) != None:
                    add = True
            if add:
                new_aln.append('>{0}.{1}\n{2}\n'.format(src, aln_count, text))
        if len(new_aln) == 2:
            new_aln.sort(key=lambda x: x[0])
            files[aln_count % split_count].writelines(new_aln)

            
    map(lambda x: x.close(), files)
    
    with open(output_file, 'w') as f:
        json.dump(filenames, f, indent=4)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Prepare parameters')
    parser.add_argument('alignment', type=str, help='Input alignment')
    parser.add_argument('working_dir', type=str, help='Working directory')
    parser.add_argument('split_count', type=int, default=40,
                        help='To how many alignments split')
    parser.add_argument('output', type=str,
                        help='Output file containing generated files')
    parser.add_argument('sequence_selector', type=str, nargs=2, 
                        help='Regular expressions for selecting strands from' + 
                        'alignment.')
    
    parsed_arg = parser.parse_args()
    main(parsed_arg.alignment, parsed_arg.working_dir, parsed_arg.split_count,
         parsed_arg.output, parsed_arg.sequence_selector)