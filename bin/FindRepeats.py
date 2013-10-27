import json
from argparse import ArgumentParser
from alignment import Fasta
from alignment.Alignment import Alignment
from collections import defaultdict
from hmm.HMM import State
from hmm.GeneralizedHMM import GeneralizedState
from adapters.TRFDriver import Repeat, TRFDriver
import itertools
from algorithm.LogNum import LogNum
from hmm.HMMLoader import HMMLoader
import hashlib
from repeats.RepeatRealigner import jsonize

model_cache = dict()

def build_model(consensus, modelParam):
    global model_cache
    mathType = modelParam["mathType"]
    model_factory = modelParam["modelFactory"]
    if consensus in model_cache:
        return model_cache[consensus]
    model = model_factory.getHMM(consensus)
    repProb = model_factory.repProb
    original_init_states = []
    original_end_states = []
    for i in range(len(model.states)):
        if model.states[i].startProbability > 0: original_init_states.append(i)
        if model.states[i].endProbability > 0: original_end_states.append(i)    
    background_state = State(mathType)
    background_state.load({
       "__name__": "State",
        "name": "BackgroundState",
        "startprob": 0.0,
        "emission": model_factory.backgroundProbability,
        "endprob": 1.0,
    })
    background_state_id = model.addState(background_state)
    init_state = GeneralizedState(mathType)
    init_state.load({
        "__name__": "GeneralizedState",
        "name": "FinderInit",
        "startprob": 1.0,
        "emission": [("", 1.0)],
        "endprob": 0.0,
        "durations": [(0, 1.0)]
    })
    init_state_id = model.addState(init_state)
    model.addTransition(
        init_state_id,
        background_state_id,
        mathType(1.0) - repProb
    )
    model.addTransition(
        background_state_id,
        background_state_id,
        mathType(1.0) - repProb
    )
    for i in original_init_states:
        prob = model.states[i].startProbability * repProb
        model.addTransition(init_state_id, i, prob)
        model.addTransition(background_state_id, i, prob)
        model.states[i].startProbability = mathType(0.0)
    for i in original_end_states:
        model.addTransition(
            i,
            background_state_id,
            model.states[i].endProbability
        )
    model.reorderStatesTopologically()
    #for state in model.states:
    #    print state.stateName
    model_cache[consensus] = model
    nm = consensus
    if len(nm) > 20:
        nm = hashlib.md5(consensus).hexdigest()
    with open('submodels/{0}.js'.format(consensus), 'w') as f:
        def LogNumToJson(obj):
            if isinstance(obj, LogNum):
                return '{0} {1}'.format(str(float(obj)),str(obj.value))
            raise TypeError
        json.dump(model.toJSON(), f, indent=4, sort_keys=True, 
                  default=LogNumToJson)
    return model

def find_repeats_in_sequence(consensus, sequence, modelParam):
    model = build_model(consensus, modelParam)
    table_tmp = model.getViterbiTable(sequence, 0, len(sequence))
    table = [None for _ in range(len(sequence) + 1)]
    for k, v in table_tmp:
        table[k] = v    
    print sequence, consensus
    #with open('tabulka.js', 'w') as f:
    #    json.dump(jsonize(table_tmp), f, indent=4)
    path = model.getViterbiPath(table)
    background_state_id = max(
        [i for i in range(len(model.states)) 
         if model.states[i].stateName == "BackgroundState"]
    )
    
    path = [x for x in path if x[2] > 0]
    print path[:10]
    print [model.states[x[0]].stateName for x in path[:10]]
    bin_path = []
    for stateID, _, sdx, _ in path:
        if sdx == 0:
            continue
        wat = 0
        if background_state_id != stateID:
            wat = 1
        bin_path.append(wat)
    print bin_path
    bin_path = zip([0] + bin_path, bin_path + [0], range(len(bin_path) + 1))
    changes = [position for a, b, position in bin_path if a != b]
    print changes
    return zip(changes, changes[1:])[::2]
 
def find_repeats_in_alignment(alignment, consensus_list, modelParam):
    ret = dict()
    print len(alignment.sequences), len(consensus_list), len(list(set(consensus_list)))
    consensus_list = list(set(consensus_list))
    count = 0;
    for i in range(len(alignment.sequences)):
        sequence = (''.join([x for x in alignment.sequences[i] if x != '-'])).upper()
        out = list()       
        for cons in consensus_list:
            pairs  = find_repeats_in_sequence(cons, sequence, modelParam)
            for start, end in pairs:
                #print "wtf", start, end, cons, len(cons), (end-start)/len(cons)
                out.append(Repeat(start, end, (end-start)/len(cons), cons, sequence[start:end]))
            count += 1
            #print count ,  (len(alignment.sequences) * len(consensus_list))
        ret[alignment.names[i]] = out
    return ret
            
# chcem mat vec, ktora vrati dict/trf veci pre zarovnanie (ako datovu strukturu)
# chcem mat vec, ktora porata statistiky na zarovnani
# Toto chcem casom aj tak presunut do zvlast subory
def compute_statistics(repeats):
    # Assuming we have alignment of two sequences
    repeats = repeats.values()
    if len(repeats) < 2: 
        return None
    repeats = repeats[:2]
    for i in range(len(repeats)):
        repeats[i].sort(key = lambda x: x.start)
    D = defaultdict(int)
    index = 0
    rep_list = repeats[1]
    for repeat in repeats[0]:
        while index < len(rep_list) and repeat.start > rep_list[index].end:
            index += 1
        ind = index
        while ind < len(rep_list) and repeat.end >= rep_list[index].start:
            D[(repeat.repetitions, rep_list[ind].repetitions)] += 1
            ind += 1
    return D

# Chcem len zobrat zarovnanie a vypocitat vsetky repeaty pre neho
def main(args):
    # TODO: build model params
    if args.model == None:
        print("You have to provide model")
        exit(1)
    loader = HMMLoader(LogNum)
    for state in loader.load(args.model)['model'].states:
        if state.onechar == 'R':
            model = state
    
    modelParam = {
        "mathType": LogNum,
        "modelFactory": model,
    } 
    driver = TRFDriver()
    trf_repeats = driver.run(args.fasta)
    alignments = Fasta.load(args.fasta, '\.[0-9]*$', Alignment)
    D = dict()
    stats = defaultdict(int)
    count = 1;
    for alignment in alignments:
        print ("Annotating alignment {0}".format(count))
        count += 1
        consensus_list = list(set([
            x.consensus for x in itertools.chain(*[
                trf_repeats[name] for name in alignment.names
            ])
        ]))
        repeats = find_repeats_in_alignment(alignment, consensus_list, modelParam)
        print repeats
        D.update(repeats)
        if args.stats != None:
            s = compute_statistics(repeats)
            for key, value in s.iteritems():
                stats[key] += value
    if args.stats != None:
        out_stats = dict()
        for k, v in stats.iteritems():
            out_stats[str(k)] = v
        with open(args.stats, 'w') as f:
            json.dump(out_stats, f, indent=4)
    for key in D:
        D[key] = [
            (x.start, x.end, x.repetitions, x.consensus, x.sequence) 
            for x in D[key]
        ]
    with open(args.output, 'w') as f:
        json.dump(D, f, indent=4)
            
        
if __name__ == "__main__":
    parser = ArgumentParser(description='Convert MAF to FASTA')
    parser.add_argument('fasta', type=str, help="Input alignment")
    parser.add_argument('output', type=str, help="Output file")
    parser.add_argument('--stats', type=str, default=None,
                        help='output file for stats')
    parser.add_argument('--model', type=str, help='Model file')
    parsed_arg = parser.parse_args()
    main(parsed_arg)