import re


def matched(name, alignment):
    r = re.compile(name)
    for s in alignment:
        if r.match(s['name']):
            return True
    return False


class MafLoader():
    def __init__(self, fname):
        self.fname = fname

    def filter_seq(self, aln, sequences):
        def check(s):
            regs = map(re.compile, sequences)
            for r in regs:
                if r.match(s['name']):
                    return True
            return False

        return filter(check, aln)

    def alignments(self):
        last_alignment = None
        last_alignment_count = 0
        with open(self.fname, 'r') as f:
            for line in f:
                if len(line) == 0:
                    continue
                if line[0] == 'a':
                    if last_alignment is not None and last_alignment_count > 0:
                        yield last_alignment, last_alignment_count
                    last_alignment = list()
                    last_alignment_count = 0
                if line[0] == 's':
                    l = line.split()
                    s = dict()
                    s['name'] = l[1]
                    s['sequence'] = l[6]
                    s['offset'] = l[2]
                    last_alignment.append(s)
                    last_alignment_count += 1
        if last_alignment is not None:
            yield last_alignment, last_alignment_count

    def filtered_alignments(self, has_sequences=None, min_length=0, remove_other=False):
        def aln_len(aln):
            return len(aln[0]['sequence'])
        for a, l in self.alignments():
            if has_sequences is not None and len(has_sequences) > 0:
                ok = True
                for s in has_sequences:
                    if not matched(s, a):
                        ok = False
                        break
                if ok and aln_len(a) < min_length:
                    ok = False
                if ok:
                    if remove_other:
                        a = self.filter_seq(a, has_sequences)
                        l = len(a)
                    yield a, l


if __name__ == '__main__':
    loader = MafLoader('data/sequences/bio/chr1.maf')
    s = loader.filtered_alignments(['hg19.chr1$', 'panTro2.chr1$', 'canFam2'], 1000, True)
    c = 0
    for i in s:
        print i[1]
        c += 1
    print c
