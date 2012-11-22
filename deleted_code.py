    def load(self, dictionary):
        HMM.load(self, dictionary)
        a = GeneralizedState(self.mathType)
        a.load({
            "__name__" : "GeneralizedState",
            "durations" : [(0, 1.0)],
            "name" : "__InitState__",
            "emission" : [("", 0.0)],
            "startprob" : self.mathType(1.0),
            "endprob" : self.mathType(0.0),
            "serialize" : False
        });
        ID = self.addState(a)
        for stateID in range(len(self.states)):
            if ID == stateID: 
                continue
            prob = self.states[stateID].getStartProbability()
            if prob > self.mathType(0.0):
                self.addTransition(ID, stateID, prob)
        a = GeneralizedState(self.mathType)
        a.load({
            "__name__" : "GeneralizedState",
            "durations" : [(0, 1.0)],
            "name" : "__EndState__",
            "emission" : [("", 0.0)],
            "startprob" : self.mathType(0.0),
            "endprob" : self.mathType(1.0),
            "serialize" : False
        })
        ID = self.addState(a)
        for stateID in range(len(self.states)):
            if ID == stateID: 
                continue
            prob = self.states[stateID].getEndProbability()
            if prob > self.mathType(0.0):
                self.addTransition(stateID, ID, prob)


       
            ret = X
            print(ret)
            print("[")
            for (_, lst) in ret:
                print("["+", ".join(["{"+ ", ".join([str(xxx)+": "+str(vvv) for (xxx,vvv) in xx.iteritems()])+"}" for xx in lst]) + "],")
            print("]")
            
            
            
            print("[")
            for (i, xx) in X:
                print(
                      "(" + \
                      str(i)  + ", {\n    " +\
                      ",\n    ".join([
                                 str(key) + ": {\n        " + \
                                 ",\n        ".join([
                                            str(kk) + ": " + \
                                            "{" + \
                                            ", ".join([str(kkk) + ": " + str(vvv)
                                             for (kkk,vvv) in vv.iteritems()]) 
                                            + "}"
                                            for (kk,vv) in value.iteritems()
                                            ]) 
                                  + "\n    }"  
                                 for (key, value) in xx.iteritems()]) + \
                      "\n}" + \
                      "),"
                )
            print("]")