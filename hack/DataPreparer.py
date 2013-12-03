__author__ = 'michal'

from hack.AnnotationLoader import AnnotationLoader
from tools.Exceptions import ParseException


class DataPreparer:
    def __init__(self, window=1):
        self._window = window
        gap_val = -1.0  # hodnota kotrou sa ma nahradit '-'
        self.m = {
            'A': 0.0,
            'C': 1.0,
            'G': 2.0,
            'T': 3.0,
            'N': 4.0,
            '-': gap_val,
        }
        self._cache = dict()

    def _get_window_range(self, position):
        return range(
            position - self.window_size//2,
            position + (1 + self.window_size)//2
        )

    def _prepare_base(self, base):
        if base not in self.m:
            raise ParseException('Invalid base')
        return self.m[base]

    def _prepare_annotations(self, annotation_dict):
        l = list()
        for k in annotation_dict:
            l.append(annotation_dict[k])
        return l

    def _prepare_sequence(self, sequence, position, annotation, c=0):
        """
        Creates data window from sequence and position

        @rtype : list
        """
        if (c, position) in self._cache:
            return self._cache[c, position]

        data = list()
        for i in self._get_window_range(position):
            if 0 <= i < len(sequence):
                b = sequence[i]
            else:
                b = '-'
            a = AnnotationLoader.get_annotation_at(annotation, position)
            data.append(self._prepare_base(b))
            data[len(data):] = self._prepare_annotations(a)

        self._cache[c, position] = data
        return data

    def prepare_data(
        self,
        sequence_x,
        position_x,
        annotation_x,
        sequence_y,
        position_y,
        annotation_y,
    ):
        data_x = self._prepare_sequence(
            sequence_x, position_x, annotation_x, 0
        )
        data_y = self._prepare_sequence(
            sequence_y, position_y, annotation_y, 1
        )
        return data_x + data_y

    @property
    def window_size(self):
        return self._window

    def clear_cache(self):
        self._cache = dict()
