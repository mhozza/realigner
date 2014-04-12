__author__ = 'michal'

from hmm.HMMLoader import HMMLoader
import track
from tools.intervalmap import intervalmap
from classifier_alignment.AnnotationConfig import Annotations, register as register_annotations


class AnnotationLoader:
    def __init__(self, loader=None):
        if loader is None:
            self.loader = HMMLoader()
            register_annotations(self.loader)


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

    def _intervals_to_interval_map(self, intervals):
        """
        Converts intervals from track to intervalmap, for searching

        currently supports binary annotations only
        """
        m = intervalmap()
        m[:] = 0
        for i in intervals:
            m[i[1]:i[2]] = 1
        return m

    def _get_annotation_from_bed(self, fname):
        """
        Reads intervals from BED file
        """
        try:
            with track.load(fname) as ann:
                ann = ann.read(fields=['start', 'end'])
                intervals = self._intervals_to_interval_map(ann)
        except Exception:
            intervals = self._intervals_to_interval_map([])
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
                sequence_annotations_config[annotation]
            )
        return res

    def get_annotations_from_model(self, model):
        if model is None:
            raise RuntimeError('No annotation model!')

        annotations = model.annotations
        annotations_x = self._get_sequence_annotations(
            annotations, model.sequences["sequence1"]
        )
        annotations_y = self._get_sequence_annotations(
            annotations, model.sequences["sequence2"]
        )
        return annotations, annotations_x, annotations_y

    def get_annotations(self, fname):
        model = self.loader.load(fname)
        return self.get_annotations_from_model(model)
