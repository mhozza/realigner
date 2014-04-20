#!/usr/bin/python
# coding=utf-8
__author__ = 'michal'
import pickle
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import constants
import config
from classifier_alignment.DataLoader import DataLoader


pic_suffix = '.eps'


def load(fname):
    try:
        with open(fname, 'r') as f:
            return pickle.load(f)
    except IOError:
        print fname, 'does not exist'


def visualize_importances(forest, fname):
    if forest is None:
        return
    importances = forest.feature_importances_
    if importances is not None:
        print importances[:len(importances)//2]
        print importances[len(importances)//2:]

    l = len(importances)

    std = np.std([tree.feature_importances_ for tree in forest.estimators_], axis=0)
    indices = np.argsort(importances)[::-1]

    # Print the feature ranking
    print("Feature ranking:")

    for f in range(l):
        print("%d. feature %d (%f)" % (f + 1, indices[f], importances[indices[f]]))

    # Plot the feature importances of the forest
    plt.figure()
    # plt.title(u"Dôležitost' atribútov")
    plt.xlabel(u'Atribút')
    plt.ylabel(u'Dôležitost\'')
    plt.bar(range(l), importances, color="r", yerr=std, align="center")
    # plt.xticks(range(l))
    plt.xlim([-1, l])
    plt.show()
    plt.savefig(fname + "_bars" + pic_suffix, transparent=True, bbox_inches='tight')


def show_importance_table(forest, prep_name, suffix, fname):
    """
    Show how to modify the coordinate formatter to report the image "z"
    value of the nearest pixel given x and y
    """
    if forest is None:
        return
    try:
        importances = forest.feature_importances_

        if prep_name == '':
            if 'indel' in suffix:
                importances = list(importances[:14]) + [0, 0] + list(importances[14:])
            data = np.reshape(importances, (2, 10))
        elif 'combined' in prep_name:
            if 'indel' in suffix:
                importances = list(importances[:14]) + [0, 0]\
                    + list(importances[14:])
            data = np.reshape(importances, (3, 10))
        elif 'fullcmp' in prep_name:
            if 'indel' in suffix:
                data = np.reshape(importances[2:], (5, 8))
            else:
                data = np.reshape(importances[4:], (5, 10))
        else:
            data = np.reshape(importances, (1, -1))

        fig, ax = plt.subplots()
        im = ax.imshow(data, cmap=cm.jet, interpolation='nearest', vmin=0)
        numrows, numcols = data.shape

        def format_coord(x, y):
            col = int(x+0.5)
            row = int(y+0.5)
            if 0 <= col < numcols and 0 <= row < numrows:
                z = data[row, col]
                return 'x=%1.4f, y=%1.4f, z=%1.4f' % (x, y, z)
            else:
                return 'x=%1.4f, y=%1.4f' % (x, y)

        ax.format_coord = format_coord
        plt.colorbar(im, orientation='horizontal')
        plt.show()
        plt.savefig(fname + "_heatmap" + pic_suffix, transparent=True, bbox_inches='tight')
    except (ValueError, TypeError) as e:
        print 'Importance table not supported', e
        print len(importances)


def load_data(preparer):
    dl = DataLoader()
    data, target, weights = list(), list(), list()
    sequences = dl.loadDirectory('data/sequences/model_train_seq/simulated')
    # sequences = dl.loadDirectory('data/sequences/train_sequences')
    for _, s_x, a_x, s_y, a_y in sequences:
        d, t, _ = preparer.prepare_training_data(
            s_x, a_x, s_y, a_y
        )
        data += d
        target += t
    return data, target


def train_error(forest, preparer):
    if forest is None:
        return
    data, target = load_data(preparer)
    print forest.score(data, target)


def avg_error(forest, preparer):
    if forest is None:
        return
    data, target = load_data(preparer)
    o = forest.predict_proba(data)[:, 1]
    d = [abs(i-j) for i, j in zip(o, target)]
    print sum(d)/len(d)


def main():
    picdir = 'mio_vysledky/clf'
    fname_template = '{}{}{}{}.clf'
    for _, clf_name, __ in config.classifiers:
        for preparer, indel_preparer, prep_name in config.preparers:
            for suffix in ('', '_indel'):
                fname = fname_template.format(
                    clf_name, prep_name, constants.window_size, suffix
                )
                clf = load(os.path.join('data/clf/', fname))
                # visualize_importances(clf, os.path.join(picdir, os.path.splitext(fname)[0]))
                # show_importance_table(
                #     clf, prep_name, suffix, os.path.join(picdir, os.path.splitext(fname)[0])
                # )
                prep = preparer(constants.window_size) if suffix == ''\
                    else indel_preparer(0, constants.window_size)
                # train_error(clf, prep)
                avg_error(clf, prep)


if __name__ == '__main__':
    main()
