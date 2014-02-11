from alignment.Realigner import Realigner
from tools.debug import jcpoint, jsonize
import json

#TODO: toto pouzivam realigner na expectation krok, asi by sa 
#      to patrilo premenovat, alebo nechat tak?
class PairExpectation(Realigner):
    
    def __init__(self):
        Realigner.__init__(self)
        self.probability = self.mathType(0.0)
        self.transitionCount = None
        self.emissionCount = None

    def prepare_data(self, *data):
        data = Realigner.prepareData(self, *data)
        arguments = 0
        (
            self.probability, 
            (self.transitionCount, self.emissionCount),
        ) = jcpoint(
            lambda: self.model.getBaumWelchCounts(
                self.X, 0, len(self.X),
                self.Y, 0, len(self.Y),
                positionGenerator=self.positionGenerator,
            ),
            'bw_counts',
            self.io_files,
            self.mathType,
        )
        return data[arguments:]

    def realign(self, x, dx, y, dy, positionGenerator=None):
        return (self.probability, self.transitionCount, self.emissionCount)
       
    def save(self, data, output_file_object):
        output_file_object.write(json.dumps(
            jsonize(data),
            sort_keys=True,
            indent=4,
        ))
        output_file_object.write('\n')
