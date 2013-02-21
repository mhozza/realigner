import json
import os
import subprocess
import argparse
from bin.Maf2Fasta import Maf2FastaGen

def main(alignment, output_file, working_directory, split_count, paralelism=20):
    
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
        file = '{dir}/{base}.fa'.format(dir=working_directory, base=base)
        fasta_generator = Maf2FastaGen(alignment)
    else:
        assert(False)
    
    parallel_dir = '{dir}/{base}_parallel'.format(
        dir=working_directory,
        base=base,
    )
    
    if not os.path.exists(parallel_dir):
        os.makedirs(parallel_dir)
    
    files = [open()]
    
    for src, aln_count, text in fasta_generator:
        files[aln_count % paralelism].write(
            '>{0}.{1}\n{2}\n'.format(src, aln_count, text)
        )
    map(lambda x: x.close(), files)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Prepare parameters')
    parser.add_argument('alignment', type=str, help='Input alignment')
    parser.add_argument('output', type=str, help='Output file')
    parser.add_argument('workink_dir', type=str, help='Working directory')
    parsed_arg = parser.parse_args()
    main()


