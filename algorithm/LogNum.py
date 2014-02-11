# pylint: disable=C0103, C0111, W0511
import math
from tools.ConfigFactory import ConfigObject
from tools.Exceptions import ParseException


def autoconvDecorator(f):
    def newFunction(self, other):
        if not isinstance(other, LogNum):
            other = LogNum(other)
        return f(self, other)
    return newFunction

NegativeInfinity = float("-inf")

class LogNum(ConfigObject):
    value = float("-inf")
    __slots__ = ('value',)
    
    def __init__(self, value = LogNum(0), log = True):
        if isinstance(value, LogNum):
            self.value = value.value
        elif log:
            try: 
                self.value = math.log(float(value))
            except ValueError:
                self.value = float("-inf")
            except TypeError:
                self.value = float("-inf")
        else:
            self.value = float(value)

    def toJSON(self):
        ret = ConfigObject.toJSON(self)
        ret['val'] = self.value
        return ret
    
    def load(self, dictionary): 
        ConfigObject.load(self, dictionary)
        if 'val' not in dictionary:
            raise ParseException("Value ('val') not found in state")
        self.value = float(dictionary['val']) 
    
    @autoconvDecorator   
    def __add__(self, other):
        if self.value == NegativeInfinity:
            return LogNum(other)
        if other.value == NegativeInfinity:
            return LogNum(self)
        #return LogNum(math.exp(self.value) + math.exp(other.value))
        if self.value > other.value:
            return LogNum(
                self.value + math.log(1 + math.exp(other.value - self.value)),
                False,
            )
        else:
            return LogNum(
                other.value + math.log(1 + math.exp(self.value - other.value)),
                False,
            )

    @autoconvDecorator 
    def __radd__(self, other):
        return self + LogNum(other)
   
    @autoconvDecorator 
    def __sub__(self, other):
        return LogNum(math.exp(self.value) - math.exp(other.value))

    
    @autoconvDecorator 
    def __mul__(self, other):
        return LogNum(self.value + other.value, False)

    
    @autoconvDecorator 
    def __div__(self, other):
        return LogNum(self.value - other.value, False)
    
    
    @autoconvDecorator 
    def __pow__(self, other):
        return LogNum(self.value*math.exp(other.value), False)
 
 
    @autoconvDecorator    
    def __lt__(self, other):
        return self.value < other.value
    
    
    @autoconvDecorator 
    def __le__(self, other):
        return self.value <= other.value
    
    @autoconvDecorator 
    def __eq__(self, other):
        if not isinstance(other, LogNum):
            other = LogNum(other)
        return self.value == other.value
    
    
    @autoconvDecorator 
    def __ne__(self, other):
        return self.value != other.value
    
    
    @autoconvDecorator 
    def __gt__(self, other):
        return self.value > other.value
    
    
    @autoconvDecorator 
    def __ge__(self, other):
        return self.value >= other.value
    
     
    def __float__(self, exp = True):
        if exp:
            return float(math.exp(self.value))
        else:
            return float(self.value)

        
    def __str__(self, exp = True):
        if exp:
            return str(math.exp(self.value))
        else:
            return str(self.value)
        
    
    def __repr__(self):
        return 'LogNum:' + str(self.value)
    
    def __hash__(self):
        return hash(self.value)


if __name__ == "__main__":
    def main():
        a = LogNum(2, True)
        b = LogNum(3, True)
        print(a+b)
        c = float(a)
        print(c)
    main()
