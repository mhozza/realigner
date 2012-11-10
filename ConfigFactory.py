import json

class ConfigObject:
    
    __classname__ = "ConfigObject"
    
    def getClassname(self):
        return self.classname
    
    
    def load(self, dictionary):
        if "__classname__" not in dictionary:
            raise "Wrong object type"
        if dictionary["__classname__"] != self.__classname__:
            raise "Wrong object file"
        
    def toJSON(self):
        return {"__classname__": self.__classname__}


class ConfigFactory:
    
    def addObject(self, classname, function):
        self.objects[classname] = function


    def objectHook(self, dictionary):
        if "__classname__" not in dictionary:
            return dictionary
        cn = dictionary["__classname__"]
        if cn in self.objects:
            obj = self.objects[cn]()
            obj.load(dictionary)
            return obj


    def load(self, filename):
        f = open(filename, "r")
        r = json.load(f, object_hook=self.objectHook)  
        return r