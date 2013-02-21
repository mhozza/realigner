import json
import os
import argparse
from bin.Maf2Fasta import Maf2FastaGen

def main(alignment, working_directory, split_count=40, output_file):
    
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
    
    files = [open('alignment_{0:04d}.fa'.format(i), 'w') 
             for i in range(split_count)]
    
    for src, aln_count, text in fasta_generator:
        files[aln_count % split_count].write(
            '>{0}.{1}\n{2}\n'.format(src, aln_count, text)
        )
        
    map(lambda x: x.close(), files)
    
    with open(output_file, 'w') as f:
        json.dump(files, f, indent=4)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Prepare parameters')
    parser.add_argument('alignment', type=str, help='Input alignment')
    parser.add_argument('working_dir', type=str, help='Working directory')
    parser.add_argument('split_count', type=str,
                        help='To how many alignments split')
    parser.add_argument('output', type=str,
                        help='Output file containing generated files')
    
    parsed_arg = parser.parse_args()
    main(parsed_arg.alignment, parsed_arg.working_dir, parsed_arg.output)