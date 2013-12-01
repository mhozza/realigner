__author__ = 'michal'
from tools.intervalmap import intervalmap
import track
from tools.ConfigFactory import ConfigFactory
from hack.AnnotationConfig import Annotations


def getInitializerObject(tp, mathType):
    def __getInitializer(dictionary):
        t = tp(mathType)
        t.load(dictionary)
        return t
    return __getInitializer


def getInitializerFunction(function, mathType):
    def __getInitializer(dictionary):
        return function(dictionary, mathType)
    return __getInitializer


class JSLoader(ConfigFactory):

    def __init__(self, mathType=float):
        ConfigFactory.__init__(self)
        self.mathType = mathType
        for obj in [
            Annotations
        ]:

            self.addFunction(obj.__name__, getInitializerObject(obj, mathType))

        for (name, constant) in [
            # STUB
        ]:
            self.addConstant(name, constant)


class AnnotationLoader:
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

#    def alnToAnnotation(self, annotations):
#        newannotations = dict()
#        for key in annotations:
#            newannotations[key] =  annotations[key].replace("-","")
#        return newannotations

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

    def get_annotations(self, fname):
        loader = JSLoader()
        annotation_config = loader.load(fname)
        annotations = annotation_config.annotations
        annotations_x = self._get_sequence_annotations(
            annotations, annotation_config.sequences["sequence1"]
        )
        annotations_y = self._get_sequence_annotations(
            annotations, annotation_config.sequences["sequence2"]
        )
        return annotations, annotations_x, annotations_y

