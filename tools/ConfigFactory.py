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
        self.functions = dict()
        self.constants = dict()
        self.dictionary = dict()
    
    def addObject(self, obj):
        self.objects[obj.__name__] = obj
        
    def addFunction(self, name ,function):
        self.functions[name] = function
        
    def addConstant(self, name, constant):
        self.constants[name] = constant
        
    def addDictionary(self, name, dictionary, check_if_exists=False):
        if check_if_exists and name in self.dictionary:
            return
        self.dictionary[name] = dictionary

    def objectHook(self, dictionary):
        """
        Object has method load. If it returns None, then the instance of 
        the object will be replaced with a dictionary. If load returns value X
        that is not none, dictionary will be replaced with X.
        
        It is possible to dynamically add dictionaries. If __name__ start with @, it means that
        it will be added as dictionary into objectHook. If it ends with ?, it will be added only
        if it is not there already
        """
        
        if "__name__" not in dictionary:
            return dictionary
        cn = dictionary["__name__"]
        if len(cn) > 0 and cn[0] == '@':
            if cn[-1] == "?":
                cnn = cn[1:-1]
                check_if_exists = True
            else:
                cnn = cn[1:]
                check_if_exists = False
            del dictionary['__name__']
            self.addDictionary(cnn, dictionary, check_if_exists)
            dictionary['__name__'] = cn
            return None
        if cn in self.objects:
            obj = self.objects[cn]()
            ret = obj.load(dictionary)
            if ret == None:
                return obj
            return ret
        elif cn in self.functions:
            ret = self.functions[cn](dictionary)
            return ret
        elif cn in self.dictionary:
            dct = self.dictionary[cn]
            if "key" not in dictionary:
                raise ParseException("Key not found in dictionary")
            ret = dct[dictionary['key']]
            return ret
        elif cn in self.constants:
            return self.constants[cn]
        else:
            return None


    def load(self, filename):
        f = open(filename, "r")
        r = json.load(f, object_hook=self.objectHook)  
        return r