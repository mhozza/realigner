import json

class ConfigObject:
    
    __classname__ = "ConfigObject"
    
    def getClassname(self):
        return self.classname
    
    def load(self, dictionary):
        raise "Not implemented"
        
    def save(self):
        return {"__classname__": self.__classname__}

class ConfigFactory:
    
    def addObject(self, classname, function):
        self.objects[classname] = function


    def objectHook(self, dictionary):
        if "__classname__" not in dictionary:
            return dictionary
        cn = dictionary["__classname__"]
        if cn in self.objects:
            return self.objects[cn](dictionary)


    def load(self, filename):
        f = open(filename, "r")
        r = json.load(f, object_hook=self.objectHook)  
        return r