# -*- coding: utf-8 -*-
__author__ = 'GRIDDIC'
import os
import numpy as np
import obr
from os.path import join as pjoin
from matplotlib import pyplot as plt
from matplotlib.mlab import griddata

def construct_initial_spectrum_tally(file_):
    tallies = obr.construct_tallies(file_)
    for tally in tallies:
        if tally.x == 0 and tally.y == 0:
            INITIAL_SPECTRUM_TALLY = tally
            break
    return INITIAL_SPECTRUM_TALLY


def sample_length_and_mode_by_file_name(file_name):
    name = os.path.split(file_name)[1]
    if len(name) == 4:
        length = int(name[2:3])
    else:
        length = int(name[2:4])
    return length, name[:2]

def norm(arr):
    arr = np.array(arr).astype(float)
    return arr/np.sum(arr)

def extend_x_y(x,y):
    if x == 0 and y == 0:
        yield x, y
        return
    if x == 0:
        yield x, y
        yield x, -y
        yield y, x
        yield -y, x
        return
    if y == 0:
        yield y, x
        yield y, -x
        yield x, y
        yield -x, y
        return
    if y == x:
        yield x, y
        yield x, -y
        yield -x, y
        yield -x, -y
        return
    yield x, y
    yield x, -y
    yield -x, y
    yield -x, -y
    yield y, x
    yield y, -x
    yield -y, x
    yield -y, -x
    return

def plot_en_spectrums_in_back_going_flow(file_name, tally_distances, colors, file_without_sample, folder_to_place_images):
    tallies = obr.construct_tallies(file_name)
    sample_length, mode = sample_length_and_mode_by_file_name(file_name)
    title = 'back flow.spectrum.sample len = ' + str(sample_length) + 'cm. mode = ' + mode
    outt = open(pjoin(folder_to_place_images,title + ".csv"), 'w')
    outt.write("distance_to_the_tally,E_min,E_max,value,dispersion\n")
    for ind in range(len(tally_distances)):
        tally_distance = tally_distances[ind]
        col = colors[ind]
        import matplotlib.pyplot as plt
        left = []
        width = []
        values = []
        dy = []
        mid = []
        if mode == 'PP':
            etalon = construct_initial_spectrum_tally(file_without_sample)

        for tally in tallies:
            if tally.x == 0 and tally.y == 0 and tally.z == 100 - sample_length - tally_distance - 1.5:
                kk = tally.values.keys()
                kk.sort()
                for en_diap in kk:
                    outt.write(str(tally_distance) + ',' + str(en_diap[0]) + ',' + str(en_diap[1]) + ',' + str(tally.values[en_diap]) + ',' + str(tally.dispersion[en_diap]) + '\n')
                    if en_diap[0] > 7:
                        continue
                    if mode == 'PP':
                        if en_diap[0] > 1:
                            continue
                    left.append(en_diap[0])
                    width.append(en_diap[1] - en_diap[0])
                    if mode == 'PP':
                        values.append((tally.values[en_diap] - etalon.values[en_diap]) * (en_diap[1] - en_diap[0]) / 4)
                    else:
                        values.append(tally.values[en_diap] * (en_diap[1] - en_diap[0]))
                    dy.append(tally.dispersion[en_diap]*values[-1]  * (en_diap[1] - en_diap[0]))
                    mid.append((en_diap[1] + en_diap[0])/2)
        plt.bar(left, values,width, color=col, yerr=dy, log=True, bottom=0.000000001, label=('distance to detector = ' + str(tally_distance) + 'cm.'))
        plt.title(r'back flow.spectrum.\\sample len = ' + str(sample_length) + r'cm. mode = ' + mode)
        plt.xlabel(r'Energy, MEV')
        plt.ylabel(r'particles, $\frac{F}{cm^2 sec MEV}$')

    outt.close()
    plt.legend()
    plt.grid()
    plt.savefig(pjoin(folder_to_place_images,title + ".png"), dpi = 300)
    print pjoin(folder_to_place_images,title + ".png")
    plt.show()
    plt.close()

def plot_sum_en_spectrum_in_back_going_flow(file_names, tally_distances, colors, PP_file_without_sample, folder_to_place_images):
    neutron_file, photon_file = file_names
    etalon = construct_initial_spectrum_tally(PP_file_without_sample)
    if os.path.split(neutron_file)[1][1:] != os.path.split(photon_file)[1][1:]:
        print "files_not_correspond_to_each_other"
        return
    tallies_n, tallies_p = obr.construct_tallies(neutron_file), obr.construct_tallies(photon_file)
    sample_length, garbage = sample_length_and_mode_by_file_name(file_names[0])
    title = 'back flow.spectrum.sample len = ' + str(sample_length) + 'cm. mode = full'
    outt = open(pjoin(folder_to_place_images, title + ".csv"), 'w')
    outt.write("distance_to_the_tally,E_min,E_max,value,dispersion\n")
    for ind in range(len(tally_distances)):
        tally_distance = tally_distances[ind]
        col = colors[ind]
        import matplotlib.pyplot as plt
        left = []
        width = []
        values = []
        dy = []
        mid = []

        for tally_ind, tally in enumerate(tallies_n):
            if tallies_n[tally_ind].x == 0 and tallies_n[tally_ind].y == 0 and tallies_n[tally_ind].z == 100 - sample_length - tally_distance - 1.5:
                if tallies_p[tally_ind].x != 0 or tallies_p[tally_ind].y != 0 or tallies_p[tally_ind].z != 100 - sample_length - tally_distance - 1.5:
                    print "wrong tallies order"
                    return
                kk = tallies_n[tally_ind].values.keys()
                kk.sort()
                for en_diap in kk:
                    outt.write(str(tally_distance) + ',' + str(en_diap[0]) + ',' + str(en_diap[1]) + ',' + str(tally.values[en_diap]) + ',' + str(tally.dispersion[en_diap]) + '\n')
                    if en_diap[0] > 7:
                        continue

                    left.append(en_diap[0])
                    width.append(en_diap[1] - en_diap[0])
                    values.append((tallies_n[tally_ind].values[en_diap] +
                                       (tallies_p[tally_ind].values[en_diap] - etalon.values[en_diap])/4)
                                        * (en_diap[1] - en_diap[0]))
                    temp = (tallies_n[tally_ind].dispersion[en_diap]*tallies_n[tally_ind].values[en_diap] + tallies_p[tally_ind].dispersion[en_diap]*(tallies_p[tally_ind].values[en_diap] - etalon.values[en_diap])/4 ) * (en_diap[1] - en_diap[0])
                    dy.append(min(temp, values[-1]))
                    mid.append((en_diap[1] + en_diap[0])/2)
        plt.bar(left, values,width, color=col, yerr=dy, log=True, bottom=0.000000001, label=('distance to detector = ' + str(tally_distance) + 'cm.'))
        plt.title(r'back flow.spectrum.\\sample len = ' + str(sample_length) + r'cm. mode = full')
        plt.xlabel(r'Energy, MEV')
        plt.ylabel(r'particles, $\frac{F}{cm^2 sec MEV}$')
        #plt.plot(mid, y, 'r--')
        #plt.savefig("images\\" + title + ".png", dpi = 300)
        #plt.show()
        #plt.close()
    outt.close()
    plt.legend()
    plt.grid()
    plt.savefig(pjoin(folder_to_place_images, title + ".png"), dpi = 300)
    print pjoin(folder_to_place_images, title + ".png")
    plt.show()
    plt.close()

def plot_dose_in_back_going_flow_for_each_file(names, tally_distanses, PP_file_without_sample, folder_to_place_images):
    etalon = construct_initial_spectrum_tally(PP_file_without_sample)
    legend = []
    for file_name in names:
        sample_length, mode = sample_length_and_mode_by_file_name(file_name)
        tallies = obr.construct_tallies(file_name)
        dosa_at_length = {}
        for tally_ind, tally in enumerate(tallies):
            if tally.x == 0 and tally.y == 0 and (100 - sample_length - tally.z - 1.5 in tally_distanses):
                if mode == 'PP':
                    dosa, dispersion = (tally.dose() - etalon.dose())/4.
                else:
                    dosa, dispersion = tally.dose()
                dosa_at_length[100 - sample_length - tally.z - 1.5] = (dosa, dispersion)
        x = sorted(dosa_at_length.keys())
        y = [dosa_at_length[k][0] for k in x]
        dy = [dosa_at_length[k][0]*dosa_at_length[k][1] for k in x]
        plt.yscale('log')
        plt.errorbar(x,y,yerr=dy)
        plt.xlabel('Distance to detector, sm.')
        plt.ylabel(r'Dose $ \frac{mkr}{sec}$')
        plt.grid('on')
        legend.append("Sample length = " + str(sample_length))
    title = "Dose in back going flow. mode = " + mode
    plt.title(title)
    plt.legend(legend, loc='best')
    plt.savefig(pjoin(folder_to_place_images,title + ".png"), dpi = 300)
    plt.show()

def plot_full_dose_in_back_going_flow_for_each_file(names, tally_distanses, PP_file_without_sample, folder_to_place_images):
    etalon = construct_initial_spectrum_tally(PP_file_without_sample)
    legend = []
    for neutron_file, photon_file in names:
        sample_length, garbage = sample_length_and_mode_by_file_name(neutron_file)
        tallies_n, tallies_p = obr.construct_tallies(neutron_file), obr.construct_tallies(photon_file)
        dosa_at_length = {}
        for tally_ind, (tally_n, tally_p) in enumerate(zip(tallies_n, tallies_p)):
            if tally_n.x == 0 and tally_n.y == 0 and (100 - sample_length - tally_n.z - 1.5 in tally_distanses):
                dosa, dispersion = tally_n.dose() + (tally_p.dose() - etalon.dose())/4.
                dosa_at_length[100 - sample_length - tally_n.z - 1.5] = (dosa, dispersion)
        x = sorted(dosa_at_length.keys())
        y = [dosa_at_length[k][0] for k in x]
        dy = [dosa_at_length[k][0]*dosa_at_length[k][1] for k in x]
        plt.yscale('log')
        plt.errorbar(x,y,yerr=dy)
        plt.xlabel('Distance to detector, sm.')
        plt.ylabel(r'Dose $ \frac{mkr}{sec}$')
        plt.grid('on')
        legend.append("Sample length = " + str(sample_length))
    title = "Dose in back going flow. mode = full."
    plt.title(title)
    plt.legend(legend, loc='best')
    plt.savefig(pjoin(folder_to_place_images,title + ".png"), dpi = 300)
    plt.show()

def extend_x_y(x,y):
    if x == 0 and y == 0:
        yield x, y
        return
    if x == 0:
        yield x, y
        yield x, -y
        yield y, x
        yield -y, x
        return
    if y == 0:
        yield y, x
        yield y, -x
        yield x, y
        yield -x, y
        return
    if y == x:
        yield x, y
        yield x, -y
        yield -x, y
        yield -x, -y
        return
    yield x, y
    yield x, -y
    yield -x, y
    yield -x, -y
    yield y, x
    yield y, -x
    yield -y, x
    yield -y, -x
    return

def plot_dose_after_the_sample(names, FOLDER_TO_SAVE_IMAGES):
    for neutron_file, photon_file in names:
        sample_length, garbage = sample_length_and_mode_by_file_name(neutron_file)
        tallies_n, tallies_p = obr.construct_tallies(neutron_file), obr.construct_tallies(photon_file)
        xs = []
        ys = []
        doses = []
        for tally_n, tally_p in zip(tallies_n, tallies_p):
            assert tally_n.is_the_same(tally_p), "Tallies are not correspond to each other."
            if abs(tally_n.x) > 20 or abs(tally_n.y) > 20:
                continue
            dose = tally_n.dose()[0] + tally_p.dose()[0]/4.
            for x,y in extend_x_y(tally_n.x,tally_n.y):
                xs.append(x)
                ys.append(y)
                doses.append(dose)
        xis = np.linspace(-20,20,100)
        yis = np.linspace(-20,20,100)
        zis = griddata(xs,ys,doses,xis,yis,interp='linear')
        CS = plt.contour(xis, yis, zis, 5, linewidths=0.5, colors='b')
        CS = plt.contourf(xis, yis, zis, 5, cmap=plt.cm.rainbow,
                  vmax=abs(zis).max(), vmin=-abs(zis).max())
        cbar = plt.colorbar()

        plt.scatter(xs,ys,c=doses, cmap=plt.cm.rainbow, vmax=abs(zis).max(), vmin=-abs(zis).max())#, s=norm(doses)*30000)
        plt.xlim(-21,21)
        plt.ylim(-21,21)
        cbar.set_label(r'$\frac{mkr}{sec}$')
        title = "Dose after the sample. sample length = " + str(sample_length) + '. mode = full'
        plt.title(title)
        plt.savefig(pjoin(FOLDER_TO_SAVE_IMAGES, title + '.png'), dpi=300)
        plt.show()

