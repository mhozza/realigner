import os
import argparse
from tools import perf
from alignment.Alignment import Alignment
from alignment import Fasta
import random


def get_random_filename():
    return '/tmp/context.{}'.format(str(random.random()))


def get_temp_filename():
    f = get_random_filename()
    while os.path.exists(f):
        f = get_random_filename()
    with open(f, "w") as ff:
        ff.write('Stub\n')
    return f


@perf.runningTimeDecorator
def main(input_filename, output_filename):
    task_ids = [1]
    if os.environ.has_key('SGE_TASK_ID'):
        sge_task_id = int(os.environ['SGE_TASK_ID'])
        if not os.environ.has_key('SGE_STEP_SIZE'):
            sge_step_size = 1
        else:
            sge_step_size = int(os.environ['SGE_STEP_SIZE'])
        sge_task_last = int(os.environ['SGE_TASK_LAST'])
        task_ids = range(
            sge_task_id,
            min(sge_task_id + sge_step_size, sge_task_last + 1)
        )
        print task_ids, sge_task_id, sge_step_size, sge_task_last
    for task_id in task_ids:
        inp_filename = input_filename.format(id=task_id - 1)
        out_filename = output_filename.format(id=task_id - 1)
        aln = list(Fasta.load(
            inp_filename, 
            '', 
            Alignment, 
            sequence_selectors=['sequence1', 'sequence2']))[0]
        tmp_filename = get_temp_filename()
        Fasta.save(zip(aln.names, aln.sequences), tmp_filename)
        os.system("muscle -in {inp} -out {out} 2> /dev/null".format(
            inp=tmp_filename,
            out=out_filename,
        ))
        os.system("cp {inp}.repeats {out}.repeats".format(
            inp=inp_filename,
            out=out_filename,
        ))
        

if __name__ == '__main__':
    parser = argparse.ArgumentParser('Run muscle inside SGE environment.')
    parser.add_argument('--input', type=str, help='Input filename.', required=True)
    parser.add_argument('--output', type=str, help='Output filename.', required=True)
    args = parser.parse_args()
    main(args.input, args.output)
    perf.printAll()
