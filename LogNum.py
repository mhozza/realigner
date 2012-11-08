import math

class LogNum:
    value = float("-inf")
        
    def __init__(self,value = float(0),log = True):
        if type(value) == LogNum:
            self.value = LogNum.value
        elif log:
            try: 
                self.value = math.log(float(value))
            except ValueError:
                self.value = float("-inf")
        else:
            self.value = float(value)
    
    def __add__(self, other):
        return LogNum(math.exp(self.value) + math.exp(other.value))
    
    def __sub__(self, other):
        return LogNum(math.exp(self.value) - math.exp(other.value))
    
    def __mul__(self, other):
        return LogNum(self.value + other.value, False)

    def __div__(self, other):
        return LogNum(self.value - other.value, False)
    
    def __pow__(self, other):
        return LogNum(self.value*math.exp(other.value), False)
    
    def __lt__(self, other):
        return self.value < other.value
    
    def __le__(self, other):
        return self.value <= other.value
    
    def __eq__(self, other):
        return self.value == other.value
    
    def __ne__(self, other):
        return self.value != other.value
    
    def __gt__(self, other):
        return self.value > other.value
    
    def __ge__(self, other):
        return self.value >= other.value
    
    def __float(self, exp = True):
        if exp:
            return float(math.exp(self.value))
        else:
            return float(self.value)
        
    def __str__(self, exp = True):
        if exp:
                return str(math.exp(self.value))
        else:
            return str(self.value)
    
        
def main():
    print("Lol")
    a = LogNum(2, True);
    b = LogNum(3, True);
    print(a+b);
    c = float(a)
    print(c)

if __name__ == "__main__":
    main()