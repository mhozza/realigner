__author__ = 'michal'

from alignment import Fasta
from random import randint, sample
from classifier_alignment.AnnotationLoader import AnnotationLoader
from tools.Exceptions import ParseException
import constants
import random
import numpy


def check_base(b):
    if b not in constants.bases or b == '-':
        raise ParseException('Invalid base')


def compute_weight(important):
    ret = float(1 + important*(constants.boost - 1))
    if ret < 1:
        print ret
    return ret


class DataPreparer:
    def __init__(self, window=1):
        self._window = window
        self.m = constants.bases

    def _get_window_range(self, position):
        return xrange(
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
                check_base(b)
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
        """Takes sequences without spaces and prepares feature data for classifier
        """
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

    def prepare_positive_data(
        self,
        sequence_x,
        sequence_xs,
        annotations_x,
        sequence_y,
        sequence_ys,
        annotations_y,
    ):
        # todo: focus on inserts
        train_data = (list(), list(), list())
        pos_x, pos_y = 0, 0
        matched_pos = set()
        important = set()

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
            else:
                important.add((pos_x, pos_y))

            if bx != '-':
                pos_x += 1
            if by != '-':
                pos_y += 1

        weights_set = set(
            j for i, p in enumerate(matched_pos)
            for j in self._get_window_range(i) if p in important
        )
        for i in xrange(len(train_data[0])):
            train_data[2].append(compute_weight(i in weights_set))

        seq_size = len(train_data[0])
        return train_data, matched_pos, seq_size, weights_set

    def prepare_negative_data_random(
        self,
        sequence_x,
        sequence_xs,
        annotations_x,
        sequence_y,
        sequence_ys,
        annotations_y,
        matched_pos,
        seq_size,
        weights_set,
    ):
        train_data = (list(), list(), list())
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
            train_data[2].append(compute_weight((len(train_data[0]) - 1) in weights_set))
        return train_data

    def prepare_negative_data(
        self,
        sequence_x,
        sequence_xs,
        annotations_x,
        sequence_y,
        sequence_ys,
        annotations_y,
        matched_pos,
        seq_size,
        weights_set,
    ):
        train_data = (list(), list(), list())

        shift_size = (1+int(numpy.random.exponential(.75)) for _ in matched_pos)
        direction = (2*random.randint(0, 1)-1 for _ in matched_pos)
        shift = (d*s for s, d in zip(shift_size, direction))

        for (x, y), s in zip(matched_pos, shift):
            y += s
            if y < 0:
                y *= -1
            if y > seq_size:
                y = 2*seq_size-y

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
            train_data[2].append(compute_weight((len(train_data[0]) - 1) in weights_set))
        return train_data

    def prepare_training_data(
        self,
        sequence_x,
        annotations_x,
        sequence_y,
        annotations_y,
    ):
        """Takes sequences with spaces and prepares training data for classifier
        """
        assert len(sequence_y) == len(sequence_x)

        sequence_xs = Fasta.alnToSeq(sequence_x)
        sequence_ys = Fasta.alnToSeq(sequence_y)

        train_data1, matched_pos, seq_size, weights_set = self.prepare_positive_data(
            sequence_x,
            sequence_xs,
            annotations_x,
            sequence_y,
            sequence_ys,
            annotations_y,
        )

        train_data0 = self.prepare_negative_data(
            sequence_x,
            sequence_xs,
            annotations_x,
            sequence_y,
            sequence_ys,
            annotations_y,
            matched_pos,
            seq_size,
            weights_set,
        )

        return train_data1[0] + train_data0[0],\
            train_data1[1] + train_data0[1],\
            train_data1[2] + train_data0[2]

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
                check_base(b)
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
        train_data = (list(), list(), list())

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
                if br != '-':
                    match_pos.add((pos_r, pos_s))
                    pos_r += 1
                pos_s += 1
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
                train_data[2].append(1.0)
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
            train_data[2].append(1.0)

        return train_data

    def get_base(self, data):
        block_size = (len(data))/(2*self.window_size-1)
        base = data[(self.window_size//2) * block_size]
        return constants.bases_reverse[base]
