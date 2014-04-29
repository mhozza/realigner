import re


def substring_in_keys(s, keys):
    r = re.compile(s)
    for k in keys:
        if r.match(k):
            return True
    return False


class MafLoader():
    def __init__(self, fname):
        self.fname = fname

    def alignments(self):
        last_alignment = None
        with open(self.fname, 'r') as f:
            for line in f:
                if len(line) == 0:
                    continue
                if line[0] == 'a':
                    if last_alignment is not None:
                        yield last_alignment
                    last_alignment = dict()
                if line[0] == 's':
                    l = line.split()
                    s = dict()
                    s['sequence'] = l[6]
                    s['offset'] = l[2]
                    last_alignment[l[1]] = s
        if last_alignment is not None:
            yield last_alignment

    def filtered_alignments(self, has_sequences=None, min_length=0):
        def aln_len(aln):
            return len(aln[aln.keys()[0]]['sequence'])
        for a in self.alignments():
            if has_sequences is not None and len(has_sequences) > 0:
                ok = True
                for s in has_sequences:
                    if not substring_in_keys(s, a.keys()):
                        ok = False
                        break
                if ok and aln_len(a) < min_length:
                    ok = False
                if ok:
                    yield a

if __name__ == '__main__':
    loader = MafLoader('data/sequences/bio/chr1.maf')
    s = loader.filtered_alignments(['hg19.chr1', 'panTro2.chr1$', 'canFam2'], 1000)
    c = 0
    for i in s:
        c += 1
    print c
