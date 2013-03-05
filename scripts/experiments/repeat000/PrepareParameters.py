import json
import argparse
import os
from bin.AgregateAnnotation import main as AggregateAnnotation
from bin.AgregateTRFOutput import main as AggregateTRFOutput

from adapters.TRFDriver import TRFDriver


def main(files, trf):
    output_files = {
        'emission': [],
        'transition': [],
        'trf_length': [],
        'trf_consensus': []
    }
    for filename in files:
        # AggregateAnnotation
        em_file = filename + '.emission.stat'
        tr_file = filename + '.transition.stat'
        le_file = filename + '.trf_length.stat'
        co_file = filename + '.trf_consensus.stat'
        AggregateAnnotation(
            filename, 0, 1,
            em_file,
            tr_file
        )
        # Run TRF
        TRF = TRFDriver(trf)
        trf_output_filename = TRF.run(filename, dont_parse=True)
        # Aggregate TRF output
        AggregateTRFOutput(
            trf_output_filename,
            le_file,
            co_file
        )
        output_files['emission'].append(em_file)
        output_files['transition'].append(tr_file)
        output_files['trf_length'].append(le_file)
        output_files['trf_consensus'].append(co_file)
    return output_files


def toList(s):
    return [s]


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='Prepare parameters')
    parser.add_argument('files', type=str, help='list_of_files')
    parser.add_argument('output_files', type=str, help='Output file')
    parser.add_argument('--start', type=int, default=0, 
                        help='Which files to select')
    parser.add_argument('--step', type=int, default=-1,
                        help='How many files to select (-1 to all)')
    parser.add_argument('--trf', type=toList, default=[
                           "/cygdrive/c/cygwin/bin/trf407b.dos.exe",
                           "C:\\cygwin\\bin\\trf407b.dos.exe",
                           "/home/mic/Vyskum/duplikacie/trf404.linux64",
                           "/home/mic/bin/trf404.linux64",
                           "/home/mic/bin/trf407b.linux64",
                           ], help="Location of tandem repeat finder binary")
    
    parsed_arg = parser.parse_args()
    
    with open(parsed_arg.files, 'r') as f:
        files = json.load(f)
        
    start = parsed_arg.start
    step = parsed_arg.step
    
    if step < 0:
        step = len(files)
    
    # Grid engine can always override parameters 
    if os.environ.has_key('SGE_TASK_FIRST'):
        start = os.environ['SGE_TASK_FIRST']
    if os.environ.has_key('SGE_STEP_SIZE'):
        step = os.environ['SGE_STEP_SIZE']

    output_files = main(files[start:start + step], parsed_arg.trf)
    with open(parsed_arg.output_files.format(index=start), 'w') as f:
        json.dump(output_files, f, indent=4)