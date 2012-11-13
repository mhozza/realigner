import math

def autoconvDecorator(f):
    def newFunction(self, other):
        if type(other) is not type(self):
            other = self.factory(other)
        return f(self, other)
    return newFunction

class LogNum:
    value = float("-inf")
        
    def __init__(self, value = float(0), log = True):
        if type(value) is LogNum:
            self.value = LogNum.value
        elif log:
            try: 
                self.value = math.log(float(value))
            except ValueError:
                self.value = float("-inf")
        else:
            self.value = float(value)
    
    def factory(self, other):
        return LogNum(other)
   

    @autoconvDecorator   
    def __add__(self, other):
        return LogNum(math.exp(self.value) + math.exp(other.value))
    
    #def __radd__(self, other):
    #    return self + LogNum(other)
   
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
        if type(other) is not LogNum:
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
        
    
        
        
if __name__ == "__main__":
    def main():
        a = LogNum(2, True)
        b = LogNum(3, True)
        print(a+b)
        c = float(a)
        print(c)
    main()