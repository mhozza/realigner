import os
from scipy.stats import norm, gaussian_kde
from classifier_alignment.ClassifierState import ClassifierState, ClassifierIndelState
from classifier_alignment.DataLoader import DataLoader

precision = 10
pseudocount = 0.001


class ClassifierAnnotationState(ClassifierState):
    def __init__(self, *args, **kwargs):
        ClassifierState.__init__(self, *args, **kwargs)

    def _emission_norm(self, c, seq_x, x, seq_y, y):
        emissions = {
            'AA': (0.79972247433521249, 0.19398256597248104, 0.14693330081697353),
            'AC': (0.69786977442433162, 0.19993235839401341, 0.0348737958785514),
            'AG': (0.68399769644379704, 0.20965793885954512, 0.03536154127545421),
            'AT': (0.68592287403589003, 0.19650898559303637, 0.031581514449457386),
            'CA': (0.71956776562221569, 0.19144215450540367, 0.03682477746616266),
            'CC': (0.76821782883324463, 0.19292709650570669, 0.1486404097061334),
            'CG': (0.67596319659456416, 0.21827935615558344, 0.03219119619558591),
            'CT': (0.6837674190311458, 0.20861418615688601, 0.0320692598463602),
            'GA': (0.67950436077946086, 0.20357059463886557, 0.027313742226557736),
            'GC': (0.68876778657195326, 0.21231922780490486, 0.03182538714790879),
            'GG': (0.76306098618937446, 0.19654678470688433, 0.16132179002560662),
            'GT': (0.72224145178919674, 0.1950193137458576, 0.030118278258748934),
            'TA': (0.70175704839967024, 0.19255956564281032, 0.031093769052554565),
            'TC': (0.68383892075903796, 0.20578812841126429, 0.03280087794171443),
            'TG': (0.71722893554958245, 0.19132284556827081, 0.03267894159248872),
            'TT': (0.78548536067420538, 0.21090228071171505, 0.1543714181197415),
        }

        loc, scale, p = emissions[(seq_x[x] + seq_y[y])]
        dc = float(round(precision*c)) / precision

        return p*(norm.cdf(dc, loc, scale) - norm.cdf(dc-1.0/precision, loc, scale))

    def _emission(self, c, seq_x, x, seq_y, y):
        emissions = {
            ('A', 'A', 0): 0.0022452709748394953,
            ('A', 'A', 1): 0.0037045521323892574,
            ('A', 'A', 2): 0.004878232720012004,
            ('A', 'A', 3): 0.006881993176089505,
            ('A', 'A', 4): 0.009619178822502501,
            ('A', 'A', 5): 0.012718408318615211,
            ('A', 'A', 6): 0.017267393789010245,
            ('A', 'A', 7): 0.02192853175797091,
            ('A', 'A', 8): 0.031027377602984355,
            ('A', 'A', 9): 0.03773630108129933,
            ('A', 'C', 0): 0.0009079063082327559,
            ('A', 'C', 1): 0.001648545777994874,
            ('A', 'C', 2): 0.0023699388151299256,
            ('A', 'C', 3): 0.003264678447383909,
            ('A', 'C', 4): 0.003965800194911091,
            ('A', 'C', 5): 0.0042164996918952835,
            ('A', 'C', 6): 0.0045121134205080935,
            ('A', 'C', 7): 0.004429720285200411,
            ('A', 'C', 8): 0.003693826105201922,
            ('A', 'C', 9): 0.0020252751263470426,
            ('A', 'G', 0): 0.001513919876860764,
            ('A', 'G', 1): 0.0022207520981721543,
            ('A', 'G', 2): 0.0027455703382888207,
            ('A', 'G', 3): 0.0034283308753906678,
            ('A', 'G', 4): 0.003995804969240688,
            ('A', 'G', 5): 0.00416409965983431,
            ('A', 'G', 6): 0.0042733773810619035,
            ('A', 'G', 7): 0.004140665440209534,
            ('A', 'G', 8): 0.0034520793919577126,
            ('A', 'G', 9): 0.0020765059879176875,
            ('A', 'T', 0): 0.0014479393023690602,
            ('A', 'T', 1): 0.002395255864401421,
            ('A', 'T', 2): 0.0031754209671009657,
            ('A', 'T', 3): 0.0035570087496387946,
            ('A', 'T', 4): 0.0037429223266851486,
            ('A', 'T', 5): 0.0038841547358839817,
            ('A', 'T', 6): 0.004011885436549496,
            ('A', 'T', 7): 0.003738469342917396,
            ('A', 'T', 8): 0.0033142264750079973,
            ('A', 'T', 9): 0.0018768297827233792,
            ('C', 'A', 0): 0.0007735998425231356,
            ('C', 'A', 1): 0.0012605229395455694,
            ('C', 'A', 2): 0.0021616382620978612,
            ('C', 'A', 3): 0.0029804484448114964,
            ('C', 'A', 4): 0.003696023960861054,
            ('C', 'A', 5): 0.004471893516993637,
            ('C', 'A', 6): 0.004814921824088313,
            ('C', 'A', 7): 0.004969545231082903,
            ('C', 'A', 8): 0.004360643201039101,
            ('C', 'A', 9): 0.0022920414563976426,
            ('C', 'C', 0): 0.0030825788226474917,
            ('C', 'C', 1): 0.0045768234765914415,
            ('C', 'C', 2): 0.005495908281628516,
            ('C', 'C', 3): 0.0073582701714436,
            ('C', 'C', 4): 0.009476900027225567,
            ('C', 'C', 5): 0.013709010364634535,
            ('C', 'C', 6): 0.01857028607230715,
            ('C', 'C', 7): 0.024387352746915423,
            ('C', 'C', 8): 0.03342049708588887,
            ('C', 'C', 9): 0.031112056914319827,
            ('C', 'G', 0): 0.0009608216395107222,
            ('C', 'G', 1): 0.00159506823742959,
            ('C', 'G', 2): 0.0023376352420853754,
            ('C', 'G', 3): 0.0028243975478956323,
            ('C', 'G', 4): 0.0034227699234540094,
            ('C', 'G', 5): 0.004315216944309386,
            ('C', 'G', 6): 0.005007979999560676,
            ('C', 'G', 7): 0.004706335507363881,
            ('C', 'G', 8): 0.0039504831461138834,
            ('C', 'G', 9): 0.0022163526140726434,
            ('C', 'T', 0): 0.0012062888788167277,
            ('C', 'T', 1): 0.0020519080803901306,
            ('C', 'T', 2): 0.002714073086581596,
            ('C', 'T', 3): 0.003323135403267564,
            ('C', 'T', 4): 0.0038294183356871983,
            ('C', 'T', 5): 0.003980636039096461,
            ('C', 'T', 6): 0.004004802953688168,
            ('C', 'T', 7): 0.003676528296311504,
            ('C', 'T', 8): 0.003325122653632989,
            ('C', 'T', 9): 0.002030038089977437,
            ('G', 'A', 0): 0.001256376905612019,
            ('G', 'A', 1): 0.0021212632574408035,
            ('G', 'A', 2): 0.0029090129597422842,
            ('G', 'A', 3): 0.003777474875031035,
            ('G', 'A', 4): 0.004242405429234001,
            ('G', 'A', 5): 0.00429799305540501,
            ('G', 'A', 6): 0.003927558694045712,
            ('G', 'A', 7): 0.004042783544577025,
            ('G', 'A', 8): 0.0031329246479365443,
            ('G', 'A', 9): 0.0016055736660231003,
            ('G', 'C', 0): 0.0010068752578683623,
            ('G', 'C', 1): 0.0017346629835037432,
            ('G', 'C', 2): 0.0022957448053155635,
            ('G', 'C', 3): 0.0028749479875863804,
            ('G', 'C', 4): 0.003635318010422233,
            ('G', 'C', 5): 0.004216240371409104,
            ('G', 'C', 6): 0.004881641974526307,
            ('G', 'C', 7): 0.0050121455260811,
            ('G', 'C', 8): 0.004011193009387973,
            ('G', 'C', 9): 0.0020379520012310448,
            ('G', 'G', 0): 0.002877312074329542,
            ('G', 'G', 1): 0.004099686683497495,
            ('G', 'G', 2): 0.0055213719199120204,
            ('G', 'G', 3): 0.007538247530492952,
            ('G', 'G', 4): 0.010090283103309112,
            ('G', 'G', 5): 0.0135018594122503,
            ('G', 'G', 6): 0.018016675224947064,
            ('G', 'G', 7): 0.02429697456320937,
            ('G', 'G', 8): 0.03361202888882815,
            ('G', 'G', 9): 0.030441663374835833,
            ('G', 'T', 0): 0.0009097729853668311,
            ('G', 'T', 1): 0.0015550351296289922,
            ('G', 'T', 2): 0.002187061557209734,
            ('G', 'T', 3): 0.0028450134243771133,
            ('G', 'T', 4): 0.003352734492438537,
            ('G', 'T', 5): 0.004088727453696068,
            ('G', 'T', 6): 0.004648532557659502,
            ('G', 'T', 7): 0.004867912150097818,
            ('G', 'T', 8): 0.004206689964464647,
            ('G', 'T', 9): 0.0023959221670758275,
            ('T', 'A', 0): 0.0015098883414125075,
            ('T', 'A', 1): 0.0024283567037990516,
            ('T', 'A', 2): 0.0030585161482264813,
            ('T', 'A', 3): 0.0035374428708959404,
            ('T', 'A', 4): 0.0039533665601866295,
            ('T', 'A', 5): 0.004178559738900305,
            ('T', 'A', 6): 0.0041170942746157685,
            ('T', 'A', 7): 0.004002822465070395,
            ('T', 'A', 8): 0.003500819292549128,
            ('T', 'A', 9): 0.0019024385960370572,
            ('T', 'C', 0): 0.0013721265126971885,
            ('T', 'C', 1): 0.0021747816696167928,
            ('T', 'C', 2): 0.0027605947393873954,
            ('T', 'C', 3): 0.0032828266797593143,
            ('T', 'C', 4): 0.0036751658658021025,
            ('T', 'C', 5): 0.0038024008052087157,
            ('T', 'C', 6): 0.004073547964168604,
            ('T', 'C', 7): 0.004194453757052431,
            ('T', 'C', 8): 0.003840055003951823,
            ('T', 'C', 9): 0.0019994478914442076,
            ('T', 'G', 0): 0.0009789091238447509,
            ('T', 'G', 1): 0.0015970128579122578,
            ('T', 'G', 2): 0.0022087484249235663,
            ('T', 'G', 3): 0.002703775508346693,
            ('T', 'G', 4): 0.0033814728045452043,
            ('T', 'G', 5): 0.004176237278843103,
            ('T', 'G', 6): 0.004659883988712892,
            ('T', 'G', 7): 0.004594714866780547,
            ('T', 'G', 8): 0.003914050217834676,
            ('T', 'G', 9): 0.0023492919875297176,
            ('T', 'T', 0): 0.002506507377573332,
            ('T', 'T', 1): 0.004365491199592855,
            ('T', 'T', 2): 0.0055688365539065055,
            ('T', 'T', 3): 0.006973515091323431,
            ('T', 'T', 4): 0.008818011071187702,
            ('T', 'T', 5): 0.012593048219844244,
            ('T', 'T', 6): 0.01665627885607403,
            ('T', 'T', 7): 0.022101156658842627,
            ('T', 'T', 8): 0.03226492254765,
            ('T', 'T', 9): 0.035545502111655046,
        }
        return emissions[(seq_x[x], seq_y[y], round((precision-1)*c))]


class ClassifierAnnotationIndelState(ClassifierIndelState):
    def __init__(self, *args, **kwargs):
        ClassifierIndelState.__init__(self, *args, **kwargs)

    def _emission_norm(self, c, seq_x, x, seq_y, y):
        emissions = {
            'A': (0.59845201689238392, 0.23642948447897971, 0.2423568649249583),
            'C': (0.64925076452599384, 0.19128106295598163, 0.2423568649249583),
            'G': (0.66471698113207489, 0.18569722267628161, 0.235686492495831),
            'T': (0.6324865900383142, 0.20456825561450012, 0.24180100055586437),
        }
        if self.state_label == 'X':
            b = seq_x[x]
        else:
            b = seq_y[y]

        loc, scale, p = emissions[b]
        dc = float(round(precision*c)) / precision

        return p*(norm.cdf(dc, loc, scale) - norm.cdf(dc-1.0/precision, loc, scale))

    def _emission(self, c, seq_x, x, seq_y, y):
        emissions = {
            ('A', 0): 0.005198361767166082,
            ('A', 1): 0.011587239922138105,
            ('A', 2): 0.01913112841857072,
            ('A', 3): 0.020835305620836624,
            ('A', 4): 0.020204082677764332,
            ('A', 5): 0.024274544108774825,
            ('A', 6): 0.0403090422024829,
            ('A', 7): 0.041562759307358706,
            ('A', 8): 0.03364673107541404,
            ('A', 9): 0.01876618157314619,
            ('C', 0): 0.000942882091696499,
            ('C', 1): 0.00474113075341553,
            ('C', 2): 0.007927327679877687,
            ('C', 3): 0.016204850048854965,
            ('C', 4): 0.03244055313849878,
            ('C', 5): 0.04382072690055593,
            ('C', 6): 0.03405333274895445,
            ('C', 7): 0.04319155195037199,
            ('C', 8): 0.03414422618258092,
            ('C', 9): 0.015040715694301285,
            ('G', 0): 0.00048082424037908104,
            ('G', 1): 0.002339209063500435,
            ('G', 2): 0.00917599355114768,
            ('G', 3): 0.0223247430967839,
            ('G', 4): 0.02460318701683969,
            ('G', 5): 0.03597606200841751,
            ('G', 6): 0.04473806644762656,
            ('G', 7): 0.05487220407398877,
            ('G', 8): 0.03924842518201544,
            ('G', 9): 0.01532786937400819,
            ('T', 0): 0.003848305339433091,
            ('T', 1): 0.007702390302105445,
            ('T', 2): 0.011059419560531808,
            ('T', 3): 0.02282536420567599,
            ('T', 4): 0.023698018769685938,
            ('T', 5): 0.02991874731614661,
            ('T', 6): 0.04149857874897969,
            ('T', 7): 0.04389424017129152,
            ('T', 8): 0.032935300578763205,
            ('T', 9): 0.012924413529076651,
        }
        if self.state_label == 'X':
            b = seq_x[x]
        else:
            b = seq_y[y]

        return emissions[(b, round((precision-1)*c))]


class SupervisedHmmClassifierAnnotationStateTraining():
    def __init__(self):
        pass

    def transitions(self, seq_x, seq_y):
        labels = list(self.labels(seq_x, seq_y))

        counts = dict()
        for state in 'MXY':
            counts[state] = dict()
            for nextstate in 'MXY':
                counts[state][nextstate] = 0

        for i, state in enumerate(labels):
            if seq_x[i] == '-' and seq_y[i] == '-':
                continue
            j = i + 1
            while j < len(labels) and seq_x[i] == '-' and seq_y[i] == '-':
                j += 1
            if i < j < len(labels):
                nextstate = labels[j]
                counts[state][nextstate] += 1

        for state in 'MXY':
            s = float(sum(counts[state].values()))
            for nextstate in 'MXY':
                counts[state][nextstate] /= s

        return {
            k+k2: v2 for k, v in counts.iteritems() for k2, v2 in v.iteritems()
        }

    def emissions_norm(self, seq_x, seq_y, ann_x, ann_y):
        labels = self.labels(seq_x, seq_y)
        classification = self.classification(seq_x, ann_x, seq_y, ann_y)
        data = dict()
        counts = {'X': 0.0, 'M': 0.0}
        for state in 'MX':
            data[state] = dict()
            for x in 'ACGT':
                if state == 'M':
                    for y in 'ACGT':
                        data[state][(x, y)] = list()
                else:
                    data[state][x] = list()

        for state, x, y, c in zip(labels, seq_x, seq_y, classification):
            # use one insert state for both X and Y - they are equivalent for now
            if state == 'Y':
                state = 'X'
            counts[state] += 1
            if state == 'X':
                if x != '-':
                    data[state][x].append(c)
                if y != '-':
                    data[state][y].append(c)
            else:
                data[state][(x, y)].append(c)

        res = dict()
        for state in 'MX':
            for x in 'ACGT':
                if state == 'M':
                    for y in 'ACGT':
                        loc, scale = norm.fit(data[state][(x, y)])
                        p = len(data[state][(x, y)]) / counts[state]
                        res[x+y] = (loc, scale, p)
                else:
                    loc, scale = norm.fit(data[state][x])
                    p = len(data[state][x]) / counts[state]
                    res[x] = (loc, scale, p)

        return res

    def emissions(self, seq_x, seq_y, ann_x, ann_y):
        labels = self.labels(seq_x, seq_y)
        classification = self.classification(seq_x, ann_x, seq_y, ann_y)
        data = dict()
        counts = {'X': 0.0, 'M': 0.0}
        for state in 'MX':
            data[state] = dict()
            for x in 'ACGT':
                if state == 'M':
                    for y in 'ACGT':
                        data[state][(x, y)] = list()
                else:
                    data[state][x] = list()

        for state, x, y, c in zip(labels, seq_x, seq_y, classification):
            # use one insert state for both X and Y - they are equivalent for now
            if state == 'Y':
                state = 'X'
            counts[state] += 1
            if state == 'X':
                if x != '-':
                    data[state][x].append(c)
                if y != '-':
                    data[state][y].append(c)
            else:
                data[state][(x, y)].append(c)

        res = dict()
        for state in 'MX':
            for x in 'ACGT':
                if state == 'M':
                    for y in 'ACGT':
                        g = gaussian_kde(data[state][(x, y)])
                        p = len(data[state][(x, y)]) / counts[state]
                        for c in xrange(precision):
                            res[(x, y, c)] = p*g.integrate_box(float(c)/precision, float(c+1.0)/precision)
                else:
                    g = gaussian_kde(data[state][x])
                    p = len(data[state][x]) / counts[state]
                    for c in xrange(precision):
                        res[(x, c)] = p*g.integrate_box(float(c)/precision, float(c+1.0)/precision)

        return res

    def starting(self):
        return [1/3.0, 1/3.0, 1/3.0]

    def get_probabilities(self, seq_x, ann_x, seq_y, ann_y):
        return\
            self.starting(),\
            self.transitions(seq_x, seq_y),\
            self.emissions(seq_x, seq_y, ann_x, ann_y)

    def labels(self, seq_x, seq_y):
        def state(i):
            if seq_x[i] == '-':
                return 'Y'
            if seq_y[i] == '-':
                return 'X'
            return 'M'

        if len(seq_x) != len(seq_y):
            return
        return (state(i) for i in xrange(len(seq_x)))

    def classification(self, seq_x, ann_x, seq_y, ann_y):
        def state(i):
            if seq_x[i] == '-':
                return 'Y'
            if seq_y[i] == '-':
                return 'X'
            return 'M'

        def merge(first, second, rule):
            l = list()
            p1 = 0
            p2 = 0
            for r in rule:
                if state(r) == 'M':
                    l.append(first[p1])
                    p1 += 1
                else:
                    l.append(second[p2])
                    p2 += 1
            return l

        if len(seq_x) != len(seq_y):
            return

        clf_match = ClassifierAnnotationState().clf
        ret_match = clf_match.multi_prepare_predict(
            (seq_x, pos, ann_x, seq_y, pos, ann_y)
            for pos in filter(lambda x: state(x) == 'M', xrange(len(seq_x)))
        )

        clf_insert = ClassifierAnnotationIndelState().clf
        ret_insert = clf_insert.multi_prepare_predict(
            (seq_x, pos, ann_x, seq_y, pos, ann_y)
            for pos in filter(lambda x: state(x) != 'M', xrange(len(seq_x)))
        )

        ret = merge(ret_match, ret_insert, xrange(len(seq_x)))

        return ret


def main():
    path_to_data = "data/"

    dl = DataLoader()
    _, s_x, a_x, s_y, a_y = dl.loadSequence(
        os.path.join(path_to_data, 'model_train_seq/simulated_alignment.fa')
    )
    training = SupervisedHmmClassifierAnnotationStateTraining()
    probabilities = training.get_probabilities(s_x, a_x, s_y, a_y)
    print(probabilities)


if __name__ == "__main__":
    main()
