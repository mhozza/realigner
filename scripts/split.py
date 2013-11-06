import argparse
from alignment.Alignment import Alignment
import json
from tools.file_wrapper import Open
from alignment import Fasta
from tools import perf

@perf.runningTimeDecorator
def main(input_file, realign_output, do_not_touch_output,
         list_of_files_output, max_length, wrap_length,
         min_seq_length):
    realign_counter = 0
    do_not_touch_counter = 0
    files = []
    for alignment in Fasta.load(input_file, '\.[0-9]*$'):
        if realign_counter % 100 == 0:
            print(realign_counter, do_not_touch_counter,alignment[0][0])
        alignment_len = len(alignment[0][1])

        annotation = alignment[2][1]

        # !!! We expect that first block is not repeat
        changes = [i for i in range(1, len(annotation))
                   if annotation[i-1] != annotation[i]] + [len(annotation)]
        Blocks = zip(changes, changes[1:]) + [(len(annotation), len(annotation) + max_length + 10)]
        Blocks = [(0, Blocks[0][0])] + Blocks
        printed = 0
        block_start = 0#None
        block_end = None
        intervals = []
        for block_id in range(1, len(Blocks), 2):
            current = Blocks[block_id]
            previous = Blocks[block_id - 1]
            if block_start == None:
                startpp = max(printed, previous[0])
                if previous[1] - startpp > wrap_length:
                    intervals.append((printed, startpp))
                    printed = startpp
                    block_start = startpp
            else:
                # Pridam tento blok, alebo zacnem novy?
                if current[1] - block_start > max_length:
                    if previous[1] - previous[0] > wrap_length * 2:
                        intervals.append((block_start, previous[0] + wrap_length))
                        intervals.append((previous[0] + wrap_length, previous[1] - wrap_length))
                        printed = previous[1] - wrap_length
                        block_start = previous[1] - wrap_length
                    else:
                        split = (previous[0] + previous[1]) / 2
                        intervals.append((block_start, split))
                        block_start = split
                        printed = split
                    #Zacnem novy
        intervals.append((printed, len(annotation)))
        assert(len(annotation) == sum([y - x for x, y in intervals]))
        for i in range(1, len(intervals)):
            assert(intervals[i - 1][1] == intervals[i][0])

        #t = list(range(0, alignment_len, max_length)) + [alignment_len]
        #intervals = zip(t, t[1:]) 

        for start, stop in intervals:
            if start >= len(annotation):
                continue
            if start == stop:
                continue
            assert(start < stop)
            ann = alignment[2][1][start:stop]
            output = None
            seq1 = alignment[0][1]
            seq2 = alignment[4][1]
            seq1_len = len(seq1) - seq1.count('-') - seq1.count('.')
            seq2_len = len(seq2) - seq2.count('-') - seq2.count('.')
            if ann.count('R') == 0 or min(seq1_len, seq2_len) < min_seq_length or ann.count('R') == len(ann):
                output = do_not_touch_output.format(id=do_not_touch_counter)
                do_not_touch_counter += 1
            else:   
                output = realign_output.format(id=realign_counter)
                realign_counter += 1
            files.append(output)
            aln = [
                (alignment[0][0], alignment[0][1][start:stop]),
                (alignment[2][0], alignment[2][1][start:stop]),
                (alignment[4][0], alignment[4][1][start:stop])
            ]
            #Fasta.save(aln, output, width=-1)
        files.append('');
        
    with Open(list_of_files_output, 'w') as f:
        json.dump(files, f, indent=4)



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input')
    # vyzera tvaru: daco.{id}.{seq_id}
    parser.add_argument('realign_output')
    parser.add_argument('do_not_touch_output')
    parser.add_argument('list_of_files_output')
    parser.add_argument('max_length', type=int, default=1000)
    parser.add_argument('wrap_length', type=int, default=50)
    parser.add_argument('min_seq_length', type=int, default=20)
    args = parser.parse_args()

    main(
        args.input,
        args.realign_output,
        args.do_not_touch_output,
        args.list_of_files_output,
        args.max_length,
        args.wrap_length,
        args.min_seq_length,
    )
    perf.printAll()
