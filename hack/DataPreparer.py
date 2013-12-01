__author__ = 'michal'

from hack.AnnotationLoader import AnnotationLoader


class DataPreparer:
    def __init__(self, window=1):
        self._window = window

    def _get_window_range(self, position):
        return range(position - self.window_size//2, position + (1 + self.window_size)//2)

    def _prepare_sequence(self, sequence, position, annotation):
        """
        Creates data window from sequence and position

        @rtype : list
        """
        data = list()
        for i in self._get_window_range(position):
            if 0 <= i < len(sequence):
                b = sequence[i]
            else:
                b = '-'
            a = AnnotationLoader.get_annotation_at(annotation, position)
            data.append(b)
            data.append(a)
        return data

    def prepare_data(self, sequence_x, position_x, annotation_x, sequence_y, position_y, annotation_y):
        data_x = self._prepare_sequence(sequence_x, position_x, annotation_x)
        data_y = self._prepare_sequence(sequence_y, position_y, annotation_y)
        return data_x + data_y

    @property
    def window_size(self):
        return self._window
