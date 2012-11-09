
class ConfigObject:
    
    classname = "ConfigObject"
    
    def getClassname(self):
        return self.classname
    
    def load(self, json):
        raise "Not implemented"
        
    def save(self):
        raise "Not implemented"

class ConfigFactory:
    
    def addObject(self, obj):
        self.objects[object.getClassname] = obj
    
    def load(self, json):
        return
        
    def save(self):
        return
    