from Exceptions import ParseException
import os.path
import re
import json
from tools.file_wrapper import Open

class ConfigObject:

    
    def load(self, dictionary):
        if "__name__" not in dictionary:
            raise ParseException("Wrong object type")
        if dictionary["__name__"] != self.__class__.__name__:
            raise ParseException("Wrong object file")
    
        
    def toJSON(self):
        return {"__name__": self.__class__.__name__}

class ConfigFactory:
    
    def __init__(self):
        self.objects = dict()
        self.functions = dict()
        self.constants = dict()
        self.dictionary = dict()
        self.fileRegExp = re.compile('^#file\((.*)\)$')
        self.filenameStack = []
        self.files = dict()
    
    
    def addObject(self, obj):
        self.objects[obj.__name__] = obj
    
        
    def addFunction(self, name ,function):
        self.functions[name] = function
    
        
    def addConstant(self, name, constant, check_if_exists=False): #TODO
        if check_if_exists:
            return
        self.constants[name] = constant
    
        
    def addDictionary(self, name, dictionary, check_if_exists=False):
        if check_if_exists and name in self.dictionary:
            return
        self.dictionary[name] = dictionary

    def addFile(self, name, filename):
        self.files[name] = filename

    def objectHook(self, dictionary):
        """
        Object has method load. If it returns None, then the instance of 
        the object will be replaced with a dictionary. If load returns value X
        that is not none, dictionary will be updated with X.
        
        It is possible to dynamically add dictionaries. If __name__ start with 
        @, it means that it will be added as dictionary into objectHook. If it
        ends with ?, it will be added only if it is not there already.
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
            dictionary['__name__'] = cnn
            self.addDictionary(cnn, dictionary, check_if_exists)
            return None
        if len(cn) > 0 and cn[0] == '#':
            res = self.fileRegExp.match(cn)
            if not res:
                raise ParseException('Unknown function')
            res = res.groups()
            if len(res) != 1:
                raise ParseException('Internal error')
            filename = res[0]
            if filename in self.files:
                filename = self.files[filename]
            if len(filename) > 0 and filename[0] == '/':
                fn = filename
            else:
                fn = os.path.join(
                    os.path.dirname(self.filenameStack[-1]),
                    filename
                )
            return self.load(fn) 
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


    def debugDump(self):
        d = dict()
        d['objects'] = self.objects
        d['constants'] = self.constants
        d['dictionary'] = self.dictionary
        d['files'] = self.files
        print(json.dumps(d, indent=4))


    def load(self, filename):
        self.filenameStack.append(filename)
        f = Open(filename, "r")
        r = json.load(f, object_hook=self.objectHook)
        self.filenameStack.pop()  
        return r
    
    def loads(self, string):
        return json.load(string, object_hook=self.objectHook)  