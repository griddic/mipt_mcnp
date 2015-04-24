# -*- coding: utf-8 -*-
__author__ = 'GRIDDIC'

import obr
import matplotlib.pyplot as plt

def main():
    tallies = obr.construct_tallies("PN10a")
    fig, ax = plt.subplots()
    x = []
    y = []
    dy = []
    for tally in tallies:
        if tally.x == 0 and tally.y == 0 and tally.z < 100:
            x.append(tally.z)
            y_, dy_ = tally.get_value_from_diaposon(2.5)
            y.append(y_)
            dy.append(dy_ * y_)
    pb = ax.bar(x, y, yerr=dy, align='center', alpha=0.4, width=3, color="blue")
    x = []
    y = []
    dy = []
    for tally in tallies:
        if tally.x == 0 and tally.y == 0 and tally.z < 100:
            x.append(tally.z)
            y_, dy_ = tally.get_value_from_diaposon(5)
            y.append(y_)
            dy.append(dy_ * y_)
    pr = ax.bar(x, y, yerr=dy, align='center', alpha=0.4, width=3, color="red")
    x = []
    y = []
    dy = []
    for tally in tallies:
        if tally.x == 0 and tally.y == 0 and tally.z < 100:
            x.append(tally.z)
            y_, dy_ = tally.get_value_from_diaposon(7.5)
            y.append(y_)
            dy.append(dy_ * y_)
    pg = ax.bar(x, y, yerr=dy, align='center', alpha=0.4, width=3, color="green")
    ax.legend( (pb, pr, pg), (' > 2.5 MeV', ' > 5 MeV', ' > 7.5 MeV') )
    #ax.set_ylabel('Particles fraction')
    ax.set_ylabel(u'Доля частиц')
    ax.set_title('Going back particles')
    #plt.yscale('log')
    plt.show()

if __name__ == "__main__":
    main()