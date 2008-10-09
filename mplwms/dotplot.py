import numpy as np
import matplotlib.pyplot as plt

sizes = [20, 40, 80]

MIN, MAX = 0.07, .996

heights = [0.6, 0.4]
widths  = [0.8, 0.2]


def to_axes_limits(limits):
    """
    convert the max values for each chromosome (or the percentages) to
    the limits for each axes.

        >>> MIN, MAX = 0.07, .996
        >>> xlimits = to_axes_limits([0.8, 0.2])
        >>> xlimits
        [(0.070000000000000007, 0.74080001592636102), (0.81080002, 0.18520004)]

    the widths + MIN should add up to reach the MAX.

        >>> assert abs(xlimits[0][1] + xlimits[1][1] + XMIN - XMAX) < .01

    these can then be used like:
        
        >>> ax = fig.add_axes([xlimits[0][0], ylimits[0][0], xlimits[0][1], ylimits[0][1])

    NOTE: the 2nd value in each tuple is the width of that subplot.

    """

    limits = np.array(limits, dtype='f')
    if limits.sum() != 1:
        limits /= limits.sum()
    for i, l in enumerate(limits):
        limits[i] *= (MAX - MIN)
        limits[i] += MIN if i == 0 else limits[i - 1]
    assert abs(limits[-1] - MAX) < .001, (limits[-1], MAX)
    limits = [MIN] +  list(limits)
    limits = zip(limits[:-1], limits[1:])
    # now we have the limits for each sub axis.
    # have to subtract to get the width/height which is what pylab
    # expects.
    return [(l[0], l[1] - l[0]) for l in limits]

widths  = to_axes_limits(widths)
heights = to_axes_limits(heights)

fig = plt.figure(figsize=(10, 10), dpi=72)

print widths, heights

a = np.arange(3)
b = np.arange(3, 6)
c = np.arange(6, 9)

import random
for i, h in enumerate(heights):
    for j, w in enumerate(widths):
        ax = fig.add_axes([w[0], h[0], w[1], h[1]])
        ax.scatter(a, b, s=sizes, facecolor=random.choice(['blue', 'green', 'red']))
        ax.set_xlim(xmin=0)
        ax.set_xlim(ymin=0)
        if j == 0:
            ax.set_ylabel('Y')
        else:
            ax.set_yticks([])

        if i == 0:
            ax.set_xlabel('X')
            print dir(ax.get_frame())
        else:
            ax.set_xticks([])

        ax.frame.set_edgecolor('#2222ff')


plt.show()

