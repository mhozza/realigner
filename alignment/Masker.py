from alignment.Alignment import Alignment
from collections import defaultdict

def get_nonoverlaping_repeats(repeat_list, length):
    # return list of non-overlaping repeats with maximal sum of scores
    repeat_list = sorted(repeat_list, key=lambda x:x.end)
    D = [0 for _ in range(length + 2)]
    I = [(None, -1) for _ in range(length + 2)]
    M = 0
    prev = 1
    for repeat in repeat_list:
        for i in range(prev, repeat.end + 1):
            if D[i] < D[i + 1]:
                D[i] = D[i - 1]
                I[i] = I[i - 1]
        prev = repeat.end
        X = D[repeat.start] + float(repeat.score)
        if X >= D[repeat.end]:
            D[repeat.end] = X
            I[i] = (repeat, repeat.start)
    ret = []
    while prev >= 0:
        r, prev = I[prev]
        ret.append(r)
    return ret

def dummy_repeat_filter_function(repeat_list, _):
    return repeat_list

def dummy_masker(alignment, repeats):
    return alignment, lambda x: x

def replace_masker(alignment, repeats, _filter=dummy_repeat_filter_function):
    repeat_types = ['hmm', 'trf', 'original_repeats']
    removed = defaultdict(list) # Tuples: From, sequence
    sequences = map(list, alignment.sequences)
    for i in range(len(sequences)):
        rep = []
        name = alignment.names[i]
        for rt in repeat_types:
            if rt not in repeats:
                continue
            if name not in repeats[rt]:
                continue
            rep.extend(repeats[rt][name])
        rep = _filter(rep, len(sequences[i]))
        for r in rep:
            if r == None:
                continue
            removed[name].append(r)
            for index in range(
                alignment.seq_to_aln[i][r.start],
                alignment.seq_to_aln[i][r.end],
            ):
                if sequences[i][index] != '-':
                    sequences[i][index] = 'N'
    def full_unmasker(aln):
        orig = full_unmasker.original_sequences
        ret = []
        repeats = set()
        for name, seq in aln:
            index = 0
            if name in orig:
                orig_sequence = orig[name]
                seq = list(seq)
                for i in range(len(seq)):
                    if seq[i] == 'N':
                        seq[i] = orig_sequence[index]
                        repeats.add(i)
                    if seq[i] != '-':
                        index += 1
                seq = ''.join(seq)
            ret.append((name, seq))
        seq = list(ret[1][1])
        for i in repeats:
            seq[i] = 'R'
        seq = ''.join(seq)
        ret[1] = (ret[1][0], seq)
        return ret
    full_unmasker.original_sequences = dict(zip(
        alignment.names,
        map(lambda x: ''.join(x).replace('-', ''), alignment.sequences),
    ))
    alignment.sequences = [''.join(x) for x in sequences]
    return alignment, full_unmasker
