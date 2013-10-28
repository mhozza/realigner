"""
Wrapper for finding repeat using our HMM and Viterbi algorithm
"""
import os
from adapters.TRFDriver import Repeat, trf_paths
from bin import FindRepeats
import json
from hmm.HMM import HMM, State
from hmm.HMMLoader import HMMLoader


class HMMDriver:
    "Wrapper for finding repeats using HMM and Viterbi algorithm"
    def __init__(
        self,
        path=trf_paths,
        mathType=float,
        model=None,
    ):
        self.path = None
        self.mathType = mathType
        self.model = None
        if model != None:
            self.setModel(model)
        if path != None:
            self.setPath(path)
    
    def setPath(self, path):
        """
        Set path
        """
        if type(path) == list:
            for p in path:
                if os.path.exists(p):
                    self.path = p
        else:
            self.path = path
            
    def setModel(self, model):
        """
        Set model or link to the model, so we have HMM generator
        """
        if type(model) == str:
            loader = HMMLoader(self.mathType)
            for state in loader.load(model)['model'].states:
                if state.onechar == 'R':
                    model = state
        if isinstance(model, HMM):
            for state in model.states:
                if state.onechar == 'R':
                    model = state
        if not isinstance(model, State):
            raise "TODO"
        self.model = model
                    
    def run(
        self,
        sequencefile,
        paramSeq=None,
        dont_parse=False,
    ):  
        output_file=sequencefile + '.hmm_repeats'
        if not os.path.exists(output_file) or \
            os.path.getmtime(sequencefile) >= os.path.getmtime(output_file):
            if dont_parse:
                return output_file
            out = json.load(output_file)
            for k, v in out.iteritems():
                out[k] = map(lambda x: Repeat(*x), v) # pass to constructor
            return out
        if dont_parse:
            return output_file
        # Annotate
        trf, _ = FindRepeats.do_find_repeats(
            sequencefile,
            paramSeq,
            self.model,
            self.mathType,
            None,
            '^.*$',
        )
        # Save repeats to disk
        save = dict()
        for k, v in trf.iteritems():
            save[k] = map(
                lambda x: [
                    x.start,
                    x.end,
                    x.repetitions,
                    x.consensus,
                    x.sequence,
                ],
                v
            )
        with open(output_file, 'w') as f:
            json.dump(save, f, indent=4)
        del save
        return trf