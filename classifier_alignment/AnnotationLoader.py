import re

__author__ = 'michal'

from hmm.HMMLoader import HMMLoader
import track
from tools.intervalmap import intervalmap
from classifier_alignment.AnnotationConfig import register as register_annotations
import constants


class AnnotationLoader:
    def __init__(self, sequence_regexp, loader=None):
        if loader is None:
            self.loader = HMMLoader()
            register_annotations(self.loader)
        self.x_regexp = sequence_regexp[0]
        self.y_regexp = sequence_regexp[1]

    @staticmethod
    def get_annotation_at(annotations, i):
        """
        Returns annotations at position i
        @param annotations:
        @param i:
        """
        base_annotation = dict()
        if annotations is not None:
            for key in annotations:
                base_annotation[key] = annotations[key][i]
        return base_annotation

    def _intervals_to_interval_map(self, intervals, offset):
        """
        Converts intervals from track to intervalmap, for searching

        currently supports binary annotations only
        """
        m = intervalmap()
        m[:] = 0
        for i in intervals:
            m[i[1]+offset:i[2]+offset] = 1
        return m

    def _get_annotation_from_bed(self, fname, offset):
        """
        Reads intervals from BED file
        """
        try:
            with track.load(fname) as ann:
                ann = ann.read(fields=['start', 'end'])
                intervals = self._intervals_to_interval_map(ann, offset)
        except Exception:
            intervals = self._intervals_to_interval_map([], 0)
        return intervals

    def _get_sequence_annotations(
        self,
        annotations,
        sequence_annotations_config
    ):
        """
        Returns annotations for one sequence
        """
        res = dict()
        for annotation in annotations:
            res[annotation] = self._get_annotation_from_bed(
                *sequence_annotations_config[annotation]
            )
        return res

    def _get_seq_name(self, names, regexp):
        r = re.compile(regexp)
        matches = [name for name in names if r.match(name)]
        if len(matches) != 1:
            raise RuntimeError(
                'Cannot get name for regexp', regexp, '. Found', len(matches), 'matches.'
            )
        return matches[0]

    def get_annotations_from_model(self, model):
        if not constants.annotations_enabled:
            return None, None, None
        if model is None:
            raise RuntimeError('No annotation model!')
        names = model.sequences.keys()
        x_name = self._get_seq_name(names, self.x_regexp)
        y_name = self._get_seq_name(names, self.y_regexp)
        annotations = model.annotations
        # print 'Using annotations for x:', x_name
        annotations_x = self._get_sequence_annotations(
            annotations, model.sequences[x_name]
        )
        # print 'Using annotations for y:', y_name
        annotations_y = self._get_sequence_annotations(
            annotations, model.sequences[y_name]
        )
        return annotations, annotations_x, annotations_y

    def get_annotations(self, fname):
        model = self.loader.load(fname)
        return self.get_annotations_from_model(model)
