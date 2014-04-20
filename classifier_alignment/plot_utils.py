# coding=utf-8

from numpy.core.function_base import linspace
import matplotlib.pyplot as plt

line_width = 3.0
linspace_size = 200


def plot(hist0, hist1, gaus0, gaus1):
    xvals = linspace(0.0, 1.0, linspace_size)
    plt.figure()
    if hist0 is not None and hist1 is not None:
        if gaus0 is not None and gaus1 is not None:
            plt.subplot(1, 2, 1)
        plt.hist(
            [
                hist1,
                hist0,
            ],
            10,
            normed=False,
            histtype='bar',
            stacked=False,
            label=[u"pozitívne", u"negatívne"]
        )
        plt.xlabel(u'Výstup klasifikátora')
        plt.ylabel(u'Počet')
        plt.legend(loc=0)
    if gaus0 is not None and gaus1 is not None:
        if hist0 is not None and hist1 is not None:
            plt.subplot(1, 2, 2)
        plt.hold(True)
        plt.plot(xvals, gaus1(xvals), label=u"pozitívne", linewidth=line_width)
        plt.plot(xvals, gaus0(xvals), label=u"negatívne", linewidth=line_width)
        plt.xlabel(u'Výstup klasifikátora')
        plt.ylabel(u'Hustota')
        plt.legend(loc=9)


def plot1(hist, gaus):
    xvals = linspace(0.0, 1.0, linspace_size)

    plt.figure()
    plt.subplot(1, 2, 1)
    # plt.hist(
    #     [
    #         hist
    #     ],
    #     10,
    #     normed=False,
    #     histtype='bar',
    #     stacked=False,
    # )

    plt.bar(
        range(len(hist)), hist
    )

    plt.legend(loc=0)
    plt.subplot(1, 2, 2)
    plt.plot(xvals, gaus(xvals), label="anotated 1", linewidth=line_width)


def plot3(hist, gaus, hist2):
    xvals = linspace(0.0, 1.0, linspace_size)

    plt.figure()
    plt.subplot(1, 3, 1)

    plt.bar(
        range(len(hist)), hist
    )

    plt.legend(loc=0)
    plt.subplot(1, 3, 2)
    plt.plot(xvals, gaus(xvals), label="anotated 1", linewidth=line_width)

    plt.subplot(1, 3, 3)
    plt.bar(
        range(len(hist2)), hist2
    )
