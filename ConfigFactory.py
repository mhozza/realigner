import json
from Exceptions import ParseException

class ConfigObject:
            
    
    def load(self, dictionary):
        if "__name__" not in dictionary:
            raise ParseException("Wrong object type")
        if dictionary["__name__"] != self.__class__.__name__:
            raise ParseException("Wrong object file")
    
        
    def toJSON(self):
        return {"__name__": self.__class__.__name__}

# TODO: Moznost pridat nejaky defaultny parametricky objekt


class ConfigFactory:
    
    def __init__(self):
        self.objects = dict()
    
    def addObject(self, obj):
        self.objects[obj.__name__] = obj


    def objectHook(self, dictionary):
        """
        Object has method load. If it returns None, then the instance of 
        the object will be replaced with a dictionary. If load returns value X
        that is not none, dictionary will be replaced with X.
        """
        if "__name__" not in dictionary:
            return dictionary
        cn = dictionary["__name__"]
        if cn in self.objects:
            obj = self.objects[cn]()
            ret = obj.load(dictionary)
            if ret == None:
                return obj
            return ret


    def load(self, filename):
        f = open(filename, "r")
        r = json.load(f, object_hook=self.objectHook)  
        return r