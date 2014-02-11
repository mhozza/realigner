# pylint: disable=C0103, C0111, W0511
from PIL import Image, ImageDraw
from collections import defaultdict
import json
import random

def get_shortest_rotation(x):
    xx = x + x
    return sorted([xx[i:i+len(x)] for i in range(len(x))])[0]

class ColorGenerator:
    def __init__(self):
        self.colors = [
            (255, 0, 0, 255), (0, 255, 0, 255), (0, 0, 255, 255),
            (255, 255, 0, 255), (255, 0, 255, 255), (0, 255, 255, 255)
        ]
        self.index = 0
        self.D = dict()

    def get(self, wat):
        if wat in self.D:
            return self.D[wat]
        if self.index < len(self.colors):
            self.D[wat] = self.colors[self.index]
            self.index += 1
        else:
            self.D[wat] = (
                random.randint(0, 255), random.randint(0, 255), 
                random.randint(0, 255), 255
            )
        return self.D[wat]


class RepeatVis():
    
    def __init__(self):
        self.repeats = defaultdict(
            lambda *x: defaultdict(lambda *x: defaultdict(list))
        )
        self.maxlen = 0

    def add_repeats(self, filename):
        
        with open(filename) as f:
            data = json.load(f)
            for sequence, repeats in data.iteritems():
                for repeat in repeats:
                    f, t, _, c, _ = tuple(repeat)
                    self.repeats[sequence][c][filename].append((f, t))
                    self.maxlen = max(self.maxlen, t + 1)

    def drawRepeats(self, sequence, width=800, _bar_hei=20, _skip=5):
        repeats = list(self.repeats[sequence].iteritems())
        repeats.sort(key=lambda x: get_shortest_rotation(x[0]))
        base_height = 0
        fls = []
        for c, v in repeats:
            base_height += len(v.keys())
            for fl, _ in v.iteritems():
                fls.append(fl)
        fls = list(set(fls))
        fls.sort()
        height = base_height * (_bar_hei + _skip)
        I = Image.new("RGBA", (width, height), (255, 255, 255, 255))
        D = ImageDraw.Draw(I) 
        for fl in fls:
            height += D.textsize(fl)[1] * 2
        del D
        del I
        I = Image.new("RGBA", (width, height), (255, 255, 255, 255))
        D = ImageDraw.Draw(I) 
        index = 0
        w_scale = float(width) / float(self.maxlen)
        colors = ColorGenerator()
        for i in fls:
            colors.get(i)
        for cons, files in repeats:
            for fl, lst in sorted(list(files.iteritems()), key=lambda x: x[0]):
                startH = index * (_bar_hei + _skip)
                endH = startH + _bar_hei
                color = colors.get(fl)
                for b, e in lst:
                    startW = int(b * w_scale)
                    endW = int(e * w_scale)
                    D.rectangle([startW, startH, endW, endH], fill=color)
                    _, h = D.textsize(cons)
                    D.text(
                        [startW + 5, startH + _bar_hei/2 - h/2],
                        cons,
                        fill = (
                            255 - color[0],
                            255 - color[1],
                            255 - color[2],
                            255
                        ),
                    )
                index += 1
        height_write = base_height * (_bar_hei + _skip)
        for t in fls:
            c = colors.get(t)
            D.text([5, height_write], t.split('.fa.')[-1], fill=c)
            height_write += 2 * D.textsize(t)[1]
        del D
        return I


