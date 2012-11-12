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

# TODO: moznost pridat aj funkciu, ktora nevrati objekt, ale nieco ine
# takze by sme vedeli davat aj default loadery na ine veci

class ConfigFactory:
    
    def __init__(self):
        self.objects = dict()
    
    def addObject(self, obj):
        self.objects[obj.__name__] = obj


    def objectHook(self, dictionary):
        if "__name__" not in dictionary:
            return dictionary
        cn = dictionary["__name__"]
        if cn in self.objects:
            obj = self.objects[cn]()
            obj.load(dictionary)
            return obj


    def load(self, filename):
        f = open(filename, "r")
        r = json.load(f, object_hook=self.objectHook)  
        return r