from PIL import Image, ImageDraw

import argparse
import sys
import os
from alignment.Alignment import Alignment
from alignment import Fasta
from tools import perf

width = 10

@perf.runningTimeDecorator
def main(input_files, output_file):
    global width
    alignments = [list(Fasta.load(name, '', Alignment, ['^sequence1', '^sequence2', '^[av].*'])) if os.path.exists(name) else None for name in input_files]
    x_len = len(Fasta.alnToSeq(alignments[0][0].sequences[0]))
    y_len = len(Fasta.alnToSeq(alignments[0][0].sequences[1]))
    I = Image.new('RGB', (x_len * width + 50, y_len * width + 50), (255, 255, 255)) 
    D = ImageDraw.Draw(I)
    colors = [(0, 0, 0), (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 0, 255), (0, 255, 255)]
    i = -1
    for aln in alignments:
        i += 1
        if aln == None:
            continue
        aln = list(aln)
        if len(aln) == 0:
            continue
        aln = aln[0]
        try:
            annotation = aln.sequences[2]
            coords = aln.getCoordPairs() 
            print coords
            x_shift = width / 2 + 25 + i
            y_shift = width / 2 + 25 + i * 2
            D.line([(x * width + x_shift, y * width + y_shift) for 
                    x, y, _ in coords], fill=colors[i])
            if annotation != None:
                for x, y, ind in coords:
                    if annotation[ind] != 'R':
                        continue
                    D.rectangle([(x * width + x_shift - width / 4, y * width + y_shift - width / 4),
                                 (x * width + x_shift + width / 4, y * width + y_shift + width / 4)], outline=colors[i]) 
        except IndexError:
            pass
        except IOError:
            pass
    del D
    I.save(output_file)

if __name__ == '__main__':
    parser = argparse.ArgumentParser('Draw alignments.')
    parser.add_argument('output', type=str, help='output image')
    parser.add_argument('alignments', type=str, help='input alignments', nargs='+')
    args = parser.parse_args()
    main(args.alignments, args.output)
    perf.printAll()
