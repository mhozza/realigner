'''
Created on May 5, 2013

@author: michal
'''
from tools.ConfigFactory import ConfigObject
from tools.Exceptions import ParseException

class Annotations(ConfigObject):
    def __init__(self):
        self.annotations = list()
        self.sequences = dict()

    def load(self, dictionary,  mathType):
        if "sequences" not in dictionary:
            raise ParseException("Sequences not in AnnotationConfig")

        self.annotations = dictionary['annotations']
        self.sequences = dict()

        for i in dictionary["sequences"]:
            self.sequences[i['name']] = dict()
            for a in i:
                self.sequences[i['name']][a['id']] = a['file']

    def toJSON(self):
        ret = ConfigObject.toJSON(self)
        ret["annotations"] = self.annotations
        ret["sequences"] = list()
        for key, value in self.sequences.iteritems():
            ann = list()
            for akey, avalue in value.iteritems():
                ann.append({'id': akey, 'value':avalue})
            ret["sequences"].append({"name":key, "annotations":ann})
        return ret

    def addSequences(self, names):
        for name in names:
            if name in self.sequences:
                return False # todo: raise exception
            self.sequences[name] = dict()

    def addAnnotationFile(self, sequence, annotationId, annotationFile):
        if sequence not in self.sequences:
            self.addSequences([sequence])
        self.sequences[sequence][annotationId] = annotationFile

    def setAnnotations(self, annotations):
        self.annotations = annotations
