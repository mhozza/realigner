import os
import argparse
import random
import sys
from bin.SplitAlignmentForContext import main as Split
def get_random_filename():
    return '/tmp/context.{}'.format(str(random.random()))


def get_temp_filename():
    f = get_random_filename()
    while os.path.exists(f):
        f = get_random_filename()
    with open(f, "w") as ff:
        ff.write('Stub\n')
    return f
     

def main(args):
    task_ids = [None]
    if os.environ.has_key('SGE_TASK_ID'):
        sge_task_id = int(os.environ['SGE_TASK_ID'])
        if 'SGE_STEP_SIZE' not in os.environ:
            sge_step_size = 1
        else:
            sge_step_size = int(os.environ['SGE_STEP_SIZE'])
        sge_task_last = int(os.environ['SGE_TASK_LAST'])
        task_ids = range(
            sge_task_id,
            min(sge_task_id + sge_step_size, sge_task_last + 1)
        )
    else:
        task_ids = [1]
        sys.stderr.write('Warning: Not running under SGE environment!\n')
    for task_id in task_ids:
        fl = get_temp_filename()
        # Not very clean way how to do it. There should be later some major refactoring
        class Stub:
            alignment=args.input_template.format(id=task_id)
            output=fl
            min_split_size=0
            max_split_size=1000000
            alignment_regexp=''
            sequence_regexp=['sequence1', 'sequence2']
        Split(Stub())
        os.system('{bin} infile={inp} outfile={out} fpfile={model} win={win}'.format(
            bin=args.binary,
            inp=fl,
            out=args.output_template.format(id=task_id),
            model=args.model,
            win=args.window,
        ))
        os.remove(fl)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Wrapper for Context (software) for gridengine.')
    parser.add_argument('--binary', type=str, help='Location of binary')
    parser.add_argument('--input_template', type=str, help='Input filename template.')
    parser.add_argument('--output_template', type=str, help='Output filename template.')
    parser.add_argument('--model', type=str, help='Model filename.')
    parser.add_argument('--window', type=int, default=10, help='Window size')
    args = parser.parse_args()
    main(args)
