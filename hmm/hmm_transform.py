import types
from copy import deepcopy

def new_emission_X(self, X, x, dx, Y, y, dy):
    return self.__class__.emission(self, X, x, dx)

def new_emission_Y(self, X, x, dx, Y, y, dy):
    return self.__class__.emission(self, Y, y, dy)

def new_durationGenerator_X(self, _, __):
    for l, p in self.__class__.durationGenerator(self):
        yield (l, 0), p

def new_durationGenerator_Y(self, _, __):
    for l, p in self.__class__.durationGenerator(self):
        yield (0, l), p

def extend_state_X(state):
    state = deepcopy(state)
    state.stateName += '_X'
    state.emission = types.MethodType(new_emission_X, state)
    state.durationGenerator = types.MethodType(new_durationGenerator_X, state)
    state.reverseDurationGenerator = types.MethodType(new_durationGenerator_X, state)
    return state

def extend_state_Y(state):
    state = deepcopy(state)
    state.stateName += '_Y'
    state.onechar = state.stateName[0]
    state.emission = types.MethodType(new_emission_Y, state)
    state.durationGenerator = types.MethodType(new_durationGenerator_Y, state)
    state.reverseDurationGenerator = types.MethodType(new_durationGenerator_Y, state)
    return state

def double_track_hmm(states, transitions, start, end, mathType=float):
    ystates = map(extend_state_Y, map(deepcopy, states))
    xstates = map(extend_state_X, states)

    states = xstates + ystates
    ytransitions = deepcopy(transitions)
    xtransitions = transitions
    transitions = []
    for suffix, wat in [('_X', xtransitions), ('_Y', ytransitions)]:
        for trans in wat:
            trans['from'] += suffix
            trans['to'] += suffix
            transitions.append(trans)
    transitions.append({
        'from': end + '_X',
        'to': start + '_Y',
        'prob': mathType(1.0),
    })
    start = start + '_X'
    end = end + '_Y'
    return states, transitions, start, end
