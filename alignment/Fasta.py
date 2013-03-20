from tools.file_wrapper import Open
import re

def loadGenerator(filename): 
    with Open(filename, 'r') as f:
        seq_name = ""
        sequence = ""
        for line in f:
            line = line.strip()
            if len(line) == 0:
                continue
            if line[0] == '>':
                if len(sequence) > 0:
                    yield (seq_name, sequence)
                seq_name = line[1:]
                sequence = ""
            else:
                sequence += line.strip()
        if len(sequence) > 0:
            yield (seq_name, sequence)


def load(filename, alignment_separator, output_formatter=lambda x:x,
         sequence_selectors=None):
    r = re.compile(alignment_separator)
    output = []
    if sequence_selectors != None:
        output = [None] * len(sequence_selectors)
    lastCategory = None
    if sequence_selectors != None:
        sequence_selectors = [re.compile(x) for x in sequence_selectors]
    for name, sequence in loadGenerator(filename):
        res = r.search(name)
        if not res:
            continue
        category= res.group()
        if lastCategory != category and lastCategory != None:
            yield output_formatter(output)
            output = []
            if sequence_selectors != None:
                output = [None] * len(sequence_selectors)
        if sequence_selectors == None:
            output.append((name, sequence))
        else:
            for i in range(len(sequence_selectors)):
                if sequence_selectors[i].search(name) != None:
                    output[i] = (name, sequence)
                    break
        lastCategory = category
    if len(output) > 0 and sum([1 for x in output if x != None]) > 0:
        yield output_formatter(output)


def saveAlignmentPiece(alignment, f, width=80):
    for (seq_name, sequence) in alignment:
        seq_length = len(sequence)
        f.write(">" + seq_name + "\n")
        if width <= 0: 
            width = seq_length
        count = seq_length / width
        for i in range(count):
            f.write(sequence[i * width: (i + 1) * width] + "\n")
        if count * width < seq_length:
            f.write(sequence[count * width:] + "\n")


def save(alignment, filename, width = 80):
    with Open(filename, "w") as f:
        saveAlignmentPiece(alignment, f, width)


def alnToSeq(sequence):
    return sequence.replace("-","")