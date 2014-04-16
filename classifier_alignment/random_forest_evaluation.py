#!/usr/bin/python
__author__ = 'michal'
import pickle
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import constants
import config


def load(fname):
    try:
        with open(fname, 'r') as f:
            return pickle.load(f)
    except IOError:
        print fname, 'does not exist'


def visualize_importances(forest):
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
    plt.title("Feature importances")
    plt.bar(range(l), importances, color="r", yerr=std, align="center")
    plt.xticks(range(l))
    plt.xlim([-1, l])
    plt.show()


def show_importance_table(forest):
    """
    Show how to modify the coordinate formatter to report the image "z"
    value of the nearest pixel given x and y
    """
    if forest is None:
        return
    try:
        importances = forest.feature_importances_
        if len(importances) < 20:
            importances = list(importances[:14]) + [0, 0] + list(importances[14:])
        data = np.reshape(importances, (2, 10))

        fig, ax = plt.subplots()
        ax.imshow(data, cmap=cm.jet, interpolation='nearest')
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
        plt.show()
    except ValueError:
        print 'Importance table not supported'


def main():
    fname_template = '{}{}{}{}.clf'

    files = [
        fname_template.format(clf_name, prep_name, constants.window_size, suffix)
        for _, clf_name, __ in config.classifiers
        for _, __, prep_name in config.preparers
        for suffix in ('', '_indel')
    ]

    for f in files:
        clf = load(os.path.join('data/clf/', f))
        visualize_importances(clf)
        show_importance_table(clf)

if __name__ == '__main__':
    main()
