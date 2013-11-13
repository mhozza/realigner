from hmm.HMMLoader import HMMLoader
import argparse
import json


def train(sequences, original_model, new_model):
    loader = HMMLoader(float)
    model = loader.load(original_model)['model']
    ID = model.statenameToID['Repeat']
    with open(sequences) as f:
        sequences = json.load(f)
    model.states[ID].trainModel(sequences)
    js = model.toJSON()
    with open(new_model, 'w') as f:
        json.dump(js, f, sort_keys=True, indent=4)
    


if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument('sequences')
    args.add_argument('original_model')
    args.add_argument('new_model')
    arguments = args.parse_args()
    train(arguments.sequences, arguments.original_model, arguments.new_model)
    
