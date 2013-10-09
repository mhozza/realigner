import json
from alignment import Fasta
import argparse
from collections import defaultdict
from tools.file_wrapper import Open
from alignment.Alignment import Alignment
from tools import perf
import os


def expand_repeats(coords, alignment):
    i = 0
    out = []
    while i < len(alignment.sequences[1]):
        if alignment.sequences[1][i] != 'R':
            out.append(coords[i])
        else:
            sets = [set(), set()]
            while (i < len(alignment.sequences[1]) and 
                   alignment.sequences[1][i] == 'R'):
                sets[0].add(coords[i][0])
                sets[1].add(coords[i][2])
                i += 1
            for x in sets[0]:
                for y in sets[1]:
                    out.append((x, -1, y))                    
        i+= 1
    return out


def remove_repeats(coords, alignment):
    i = 0
    out = []
    while i < len(alignment.sequences[1]):
        if alignment.sequences[1][i] != 'R':
            out.append(coords[i])
        i+= 1
    return out



identity = lambda x, *_: x


@perf.runningTimeDecorator
def main(correct_file, aln_file, output_file, interval=None):
    task_ids = [None]
    if os.environ.has_key('SGE_TASK_ID'):
        if os.environ['SGE_TASK_ID'] != 'undefined':
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
    if interval != None:
        task_ids = range(interval[0], interval[1] + 1)
    for task_id in task_ids:
        separator = ''
        output = {}
        for fun, tp in [(identity, 'standard'), (expand_repeats, 'expanded_repeats'), (remove_repeats, 'removed_repeats')]:
            try:
                for correct, alignment in zip(
                    Fasta.load(correct_file.format(id=task_id - 1), separator, Alignment),
                    Fasta.load(aln_file.format(id=task_id - 1), separator, Alignment)
                ):
                    correct_len = len(correct.getCoordPairs(False))
                    total_len = correct_len * 2 - correct.sequences[0].count('-') - correct.sequences[2].count('-')
                    ccc = fun(correct.getCoordPairs(False), correct)
                    if tp == 'removed_repeats':
                        correct_len = len(ccc)
                        total_len = 0
                        for v1, _, v2 in ccc:
                            if v1 >= 0:
                                total_len += 1
                            if v2 >= 0:
                                total_len += 1
                    acc = alignment.getCoordPairs(False)
                    cc = map(lambda x: (x[0], x[2]), ccc)
                    if len(acc[0]) == 3:
                        ac = map(lambda x: (x[0], x[2]), acc)
                    elif len(acc[0]) ==2:
                        ac = acc
                    else: 
                        ac = None
                    c = set(cc)
                    a = set(ac)
                    
                    intersect = c.intersection(a)
                    not_in_c = c.difference(a)
                    not_in_a = a.difference(c)
                    symm_diff = c.symmetric_difference(a)

                    score = 0
                    for v1, v2 in intersect:
                        if v1 >= 0: 
                            score += 1
                        if v2 >= 0: 
                            score += 1
                  
                    
                    dists_correct = defaultdict(int)
                    dists_total = defaultdict(int)
                    position = dict()
                    dists = [99999999] * len(correct.sequences[1])
                    dst = 9999999
                    for x, a, y in ccc:
                        position[(x,y)] = a
                    for i in range(len(correct.sequences[1])):
                        if correct.sequences[1][i] == 'R':
                            dst = 0
                        else:
                            dst += 1
                        dists[i] = min(dists[i], dst)
                    for i in reversed(range(len(correct.sequences[1]))):
                        if correct.sequences[1][i] == 'R':
                            dst = 0
                        else:
                            dst += 1
                        dists[i] = min(dists[i], dst)

                    for pos in c:
                        d = dists[position[pos]]
                        if d == 0: 
                            continue
                        dists_total[d] += 1
                        if pos in ac:
                            dists_correct[d] += 1
                    
                        


                    def getRepeatAnnotation(coord, annotation):
                        if len(coord[0]) != 3:
                            return set()
                        ret = set()
                        for x, a, y in coord:
                            if annotation[a] == 'R':
                                if x >= 0:
                                   ret.add((x, -1))
                                if y >= 0:
                                    ret.add((-1, y))
                        return ret

                    crann = getRepeatAnnotation(correct.getCoordPairs(False), correct.sequences[1]) 
                    arann = getRepeatAnnotation(alignment.getCoordPairs(False), alignment.sequences[1]) 

                    def getRepeatBlocks(coord, annotation):
                        if len(coord[0]) != 3:
                            return set()
                        ret = set()
                        x = set()
                        y = set()
                        for _x, a, _y in coord:
                            if annotation[a] == 'R':
                                if _x >= 0: 
                                    x.add(_x)
                                if _y >= 0:
                                    y.add(_y)
                            else:
                                if len(x) + len(y) > 0:
                                    if len(x) == 0:
                                        x.add(-1)
                                    if len(y) == 0:
                                        y.add(-1)
                                    ret.add(((min(x), max(x) + 1), (min(y), max(y) + 1)))
                                    x = set()
                                    y = set()
                        if len(x) + len(y) > 0:
                            if len(x) == 0:
                                x.add(-1)
                            if len(y) == 0:
                                y.add(-1)
                            ret.add(((min(x), max(x) + 1), (min(y), max(y) + 1)))
                            x = set()
                            y = set()
                        return ret

                    cbann = getRepeatBlocks(correct.getCoordPairs(False), correct.sequences[1])
                    abann = getRepeatBlocks(alignment.getCoordPairs(False), alignment.sequences[1])
                    
                    def dst(x1, x2):
                        if x1 == -1:
                            return 0
                        return x2 - x1

                    def getPoints(s):
                        return sum([dst(x1,x2) + dst(y1,y2) for ((x1, x2), (y1, y2)) in s])

                    # Find long segments that are correctly aligned
                    cseg = [1 if x in c else 0 for x in ac]
                    seg_len = []
                    length = 0
                    segment_length_histogram = defaultdict(int)
                    for x in cseg:
                        if x == 0 and length != 0:
                            segment_length_histogram[length] += 1
                        length = length * x + x
                        seg_len.append(length)
                    if length > 0:
                        segment_length_histogram[length] += 1
                 
                    getPoints = len
                    output[tp] = {
                        'corect': correct_file,
                        'alignment': aln_file,
                        'c-lenght': len(cc),
                        'a-length': len(ac),
                        'intersect': len(intersect),
                        '%correct': 100.0 - float(len(intersect) * 100) / correct_len if correct_len > 0 else 100,
                        '+mistakes': len(intersect),
                        '+len': correct_len,
                        '+RepTP': len(crann & arann),
                        '+RepTN': total_len - len(crann | arann),
                        '+RepFP': len(arann - crann),
                        '+RepFN': len(crann - arann),
                        '+BlkTP': getPoints(cbann & abann),
                        '+BlkTN': 0,
                        '+BlkFP': getPoints(abann - cbann),
                        '+BlkFN': getPoints(cbann - abann),
                        '%score': float(score) * 100 / total_len if total_len > 0 else 0,
                        'c-a': len(not_in_c),
                        'a-c': len(not_in_a),
                        'symmetric_difference': len(symm_diff),
                        'correct_len_histogram': segment_length_histogram,
                        '@+dists_correct': dists_correct,
                        '@+dists_total': dists_total,
                    }
                    if correct_len == 0:
                        del output[tp]['%correct']
                    if total_len == 0:
                        del output[tp]['%score']
            except IOError:
                pass
                        
        with Open(output_file.format(id=task_id - 1), 'w') as f:
            json.dump(output, f, indent=4)
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Analyze alignment.')
    parser.add_argument('correct', type=str, help='Correct alignment')
    parser.add_argument('aln', type=str, help='Alignment to analyze')
    parser.add_argument('output_file', type=str, help='Output file')
    parser.add_argument('--interval', type=int, nargs=2, default=None,
                        help='Interval of ids (overide SGE settings');
    parsed_arg = parser.parse_args()
    main(parsed_arg.correct, parsed_arg.aln, parsed_arg.output_file,
         parsed_arg.interval)
    perf.printAll() 
