__author__ = 'michal'

from alignment import Fasta
from random import randint, sample
from classifier_alignment.AnnotationLoader import AnnotationLoader
from tools.Exceptions import ParseException
import constants


class DataPreparer:
    def __init__(self, window=1):
        self._window = window
        self.m = constants.bases

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
            data.append(self._prepare_base(b))
            data[len(data):] = self._prepare_annotations(a)

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
            sequence_x, position_x, annotation_x
        )
        data_y = self._prepare_sequence(
            sequence_y, position_y, annotation_y
        )
        return data_x + data_y

    @property
    def window_size(self):
        return self._window

    def prepare_training_data(
        self,
        sequence_x,
        annotations_x,
        sequence_y,
        annotations_y,
    ):
        train_data = (list(), list())
        sequence_xs = Fasta.alnToSeq(sequence_x)
        sequence_ys = Fasta.alnToSeq(sequence_y)

        pos_x, pos_y = 0, 0

        matched_pos = set()
        assert len(sequence_y) == len(sequence_x)

        for i in range(len(sequence_x)):
            bx, by = sequence_x[i], sequence_y[i]
            if bx != '-' and by != '-':
                matched_pos.add((pos_x, pos_y))
                d = self.prepare_data(
                    sequence_xs,
                    pos_x,
                    annotations_x,
                    sequence_ys,
                    pos_y,
                    annotations_y,
                )
                if d is not None:
                    train_data[0].append(d)
                    train_data[1].append(1)

            if bx != '-':
                pos_x += 1
            if by != '-':
                pos_y += 1

        seq_size = len(train_data[0])
        for i in range(seq_size):
            x = None
            while x is None:
                x = randint(
                    self.window_size//2,
                    len(sequence_xs) - 1 - self.window_size//2,
                )
            y = None
            while y is None or (x, y) in matched_pos:
                y = randint(
                    self.window_size//2,
                    len(sequence_ys) - 1 - self.window_size//2,
                )

            d = self.prepare_data(
                sequence_xs,
                x,
                annotations_x,
                sequence_ys,
                y,
                annotations_y,
            )
            train_data[0].append(d)
            train_data[1].append(0)

        return train_data

    def get_base(self, data):
        block_size = len(data)/(2*self.window_size)
        base_x = data[(self.window_size//2) * block_size]
        base_y = data[(self.window_size + (self.window_size//2)) * block_size]
        return constants.bases_reverse[base_x], constants.bases_reverse[base_y]


class IndelDataPreparer(DataPreparer):
    def __init__(self, insert_sequence, window=1):
        DataPreparer.__init__(self, window)
        self.insert_sequence = insert_sequence

    def _get_space_window_range(self, position):
        return range(
            position - self.window_size//2,
            position + (1 + self.window_size)//2 - 1
        )

    def _prepare_space_sequence(self, sequence, position, annotation):
        """
        Creates data window from sequence and position

        @rtype : list
        """
        data = list()
        for i in self._get_space_window_range(position):
            if 0 <= i < len(sequence):
                b = sequence[i]
            else:
                b = '-'
            a = AnnotationLoader.get_annotation_at(annotation, position)
            data.append(self._prepare_base(b))
            data[len(data):] = self._prepare_annotations(a)

        return data

    def prepare_data(
        self,
        sequence_x,
        position_x,
        annotation_x,
        sequence_y,
        position_y,
        annotation_y,
        reference=None,
    ):
        if reference is None:
            reference = self.insert_sequence

        args = [
            (sequence_x, position_x, annotation_x),
            (sequence_y, position_y, annotation_y),
        ]

        data_r = self._prepare_sequence(*args[reference])
        data_s = self._prepare_space_sequence(*args[1-reference])
        return data_r + data_s

    def prepare_training_data(
        self,
        sequence_x,
        annotations_x,
        sequence_y,
        annotations_y,
    ):
        train_data = (list(), list())

        if self.insert_sequence == 0:
            reference = sequence_x
            annotations_r = annotations_x
            space = sequence_y
            annotations_s = annotations_y
        else:
            reference = sequence_y
            annotations_r = annotations_y
            space = sequence_x
            annotations_s = annotations_x

        sequence_rs = Fasta.alnToSeq(reference)
        sequence_ss = Fasta.alnToSeq(space)

        pos_s, pos_r = 0, 0

        match_pos = set()
        for i in range(len(space)):
            br, bs = reference[i], space[i]
            if bs != '-':
                pos_s += 1
                if br != '-':
                    match_pos.add((pos_r, pos_s-1))
                    pos_r += 1
                continue
            if br == '-':
                continue

            d = self.prepare_data(
                sequence_rs,
                pos_r,
                annotations_r,
                sequence_ss,
                pos_s,
                annotations_s,
                0,
            )
            if d is not None:
                train_data[0].append(d)
                train_data[1].append(1)
            pos_r += 1

        matches = sample(match_pos, len(train_data[0]))
        for x, y in matches:
            d = self.prepare_data(
                sequence_rs,
                x,
                annotations_r,
                sequence_ss,
                y,
                annotations_s,
                0,
            )

            train_data[0].append(d)
            train_data[1].append(0)

        return train_data

    def get_base(self, data):
        block_size = (len(data))/(2*self.window_size-1)
        base = data[(self.window_size//2) * block_size]
        return constants.bases_reverse[base]
