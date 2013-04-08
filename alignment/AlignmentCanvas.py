from PIL import Image, ImageDraw
import functools
from collections import defaultdict

def alignment_column_to_annotation(column):
    column = tuple([x if x == '-' else 'M' for x in column])
    if column == ('-', 'M'):
        return 'Y'
    elif column == ('M', '-'):
        return 'X'
    elif column == ('M', 'M'):
        return 'M'
    else:
        return '-'
    

class AlignmentCanvas():
    
    def __init__(self):
        self.sequences = {"X": {"sequence": ""}, "Y": {"sequence": ""}}
        # 5 tuples: 
        # 3 tuples:
        self.lines = []
        
    
    def add_sequence(self, strand, sequence):
        self.sequences[strand] = {"sequence": sequence}
        
    def add_annotation(self, strand, track, annotation):
        if track not in self.sequences[strand]:
            self.sequences[strand][track] = []
        self.sequences[strand][track].append(annotation)
        
    def add_line(self, param):
        self.lines.append(param)
    
    def add_original_alignment(self, aln):
        last = ""
        start = -1
        original_annotation = map(
            alignment_column_to_annotation,
            zip(aln.sequences[0], aln.sequences[1])
        )
        original_annotation += "?"
        for (char, i) in zip(original_annotation,
                             range(len(original_annotation))):
            if char != last:
                if start >=0:
                    color = (255, 255, 0, 255)
                    if last == 'R':
                        color = (255, 0, 0, 255)
                    elif last == 'M':
                        color = (0, 255, 0, 255)
                    if (aln.aln_to_seq[0][start] < 
                        aln.aln_to_seq[0][i - 1]):
                        self.add_annotation('X', 'O', 
                                              (aln.aln_to_seq[0][start],
                                               aln.aln_to_seq[0][i - 1],
                                               color))
                    if (aln.aln_to_seq[1][start] < 
                        aln.aln_to_seq[1][i - 1]):
                        self.add_annotation('Y', 'O',
                                              (aln.aln_to_seq[1][start],
                                               aln.aln_to_seq[1][i - 1],
                                               color))
                start = i
                last = char
                 
    def add_repeat_finder_annotation(self, strand, track, annotation, color):
        for TRF in annotation:
            self.add_annotation(
                strand,
                track,
                (TRF.start, TRF.end, color)
            )
    
    def add_alignment_line(self, priority, color, width, segments):
        self.add_line((priority, color, width, segments))
        
    
    def add_borders_line(self, priority, color, width, segments):
        d = defaultdict(list)
        s = set()
        for x, y in segments:
            s.add(x)
            d[x].append(y)
        lower = []
        upper = []
        for x in sorted(list(s)):
            lower.append((x, min(d[x])))
            upper.append((x, max(d[x])))
        self.add_line((priority, color, width, upper))
        self.add_line((priority, color, width, lower))
            
            
    def add_posterior_table(self, table):
        colors = [(255, 255, 0, 255), (0, 255, 0, 255), (0, 0, 255, 255),
                  (255, 0, 0, 255)]
        inf = float("-inf");
        for x in range(len(table)):
            for y, val in table[x].iteritems():
                for (state, dx, dy), prob in val.iteritems():
                    dd = dx + dy
                    if dd == 0:
                        weight = -99999999999
                    else:
                        weight = prob * dd
                    if weight > inf: 
                        self.add_line((weight, colors[state], 1,
                                       [(x, y), (x - dx, y - dy)]))
    
    
    def draw(self, output_filename, width, height,
             annotation_width=30, annotation_border=5):
        
        I = Image.new("RGBA", (width, height), (255, 255, 255, 255))
        D =  ImageDraw.Draw(I)
        x_len = len(self.sequences['X']['sequence'])
        y_len = len(self.sequences['Y']['sequence']) 
        # determine graph canvas
        w = width
        h = height
        s = set()
        for k in self.sequences['X']:
            s.add(k)
        for k in self.sequences['Y']:
            s.add(k)
        s.remove('sequence')
        s = list(s)
        s.sort()
        ann_dict = dict()
        for i in range(len(s)):
            ann_dict[s[i]] = i
        n_xann = n_yann = len(s)
        w -= (annotation_width + annotation_border) * n_xann + \
            annotation_border
        h -= (annotation_width + annotation_border) * n_yann + \
            annotation_border
        
        imagemult = min(float(w) / x_len, float(h) / y_len)
        canvas = ((width - w, h), (width, 0))
        
       
        def translate(canvas, imagemult, point):
            assert(len(point) == 2)
            bx, by = canvas[0]
            x, y = (imagemult * point[0], imagemult * point[1])
            if canvas[0][0] > canvas[1][0]:
                x *= -1
            if canvas[0][1] > canvas[1][1]:
                y *= -1
            ww = abs(canvas[0][0] - canvas[1][0])
            hh = abs(canvas[0][1] - canvas[1][1])
            if ww < hh:
                x, y = y, x
            return (int(bx + x), int(by + y))
        canvasTranslator = functools.partial(translate, canvas, imagemult)
        
        annotationTranslators = {"X": dict(), "Y": dict()}
        for i in range(n_xann):
            start = (annotation_border + annotation_width) * i + \
                annotation_border
            stop = start + annotation_width
            canvas = ((width - w, h + start), (width,h + stop))
            annotationTranslators['X'][s[i]] = \
                functools.partial(translate, canvas, imagemult)
        for i in range(n_yann):
            start = (annotation_border + annotation_width) * i + \
                annotation_border
            stop = start + annotation_width
            canvas = ((width - w - start, h), (width - w - stop,0))
            annotationTranslators['Y'][s[i]] = \
                functools.partial(translate, canvas, imagemult)
                
        self.lines.sort(key=lambda x: x[0])
        for _, color, _width, segments in self.lines:
            D.line(map(canvasTranslator, segments), fill=color, width=_width)
        
        for seq, v in self.sequences.iteritems():
            for name, annotations in v.iteritems():
                if name == 'sequence':
                    continue
                translator = annotationTranslators[seq][name]
                for start, stop, color in annotations:
                    rect = [(start, 0), 
                            (stop, (annotation_width / imagemult))]
                    rect = map(translator, rect)
                    if name == 'R':
                        fl = (0, 0, 0, 255)
                    else:
                        fl = color
                    if color in [(0, 0, 0, 255), (255, 0, 0, 255)]:
                        if seq == 'X':
                            D.line([(rect[0][0], h), (rect[0][0], 0)], fill=fl)
                            D.line([(rect[1][0], h), (rect[1][0], 0)], fill=fl)
                        elif seq == 'Y':
                            D.line([(width - w, rect[0][1]),
                                    (width, rect[0][1])], fill=fl)
                            D.line([(width - w, rect[1][1]), 
                                    (width, rect[1][1])], fill=fl)
                    D.rectangle(rect, outline=(0, 0, 0, 255), 
                                    fill=color) 
        print w, h, x_len, y_len
        del D  
        I.save(output_filename)
