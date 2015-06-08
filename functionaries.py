# -*- coding: utf-8 -*-
__author__ = 'GRIDDIC'
import os
import numpy as np
import obr
from os.path import join as pjoin
from matplotlib import pyplot as plt
from matplotlib.mlab import griddata

FIGURES_SIZE = (10,6)
LEGENDS_SIZE = 12

def __parse_name(file_name):
    ans = {}
    name = os.path.split(file_name)[1]
    ans['mode'] = name[:2]
    ans['is_carbon'] = name.find('C') != -1
    if ans['is_carbon']:
        ans['length'] = int(name[3:-1])
    else:
        ans['length'] = int(name[2:-1])
    return ans

def parse_file_name(file_name, what_to_return):
    ans = []
    p = __parse_name(file_name)
    for ret in what_to_return:
        ans.append(p[ret])
    return ans


def construct_initial_spectrum_tally(file_, x, y, z):
    tallies = obr.construct_tallies(file_)
    INITIAL_SPECTRUM_TALLY = None
    for tally in tallies:
        if tally.x == x and tally.y == y and tally.z == z:
            INITIAL_SPECTRUM_TALLY = tally
            break
    assert INITIAL_SPECTRUM_TALLY is not None, "No tally with such coordinates."
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
    #ax = plt.figure()
    for ind in range(len(tally_distances)):
        tally_distance = tally_distances[ind]
        col = colors[ind]
        import matplotlib.pyplot as plt
        left = []
        width = []
        values = []
        dy = []
        mid = []
        x = 0
        y = 0
        z = 100 - tally_distance - 1.5

        etalon = construct_initial_spectrum_tally(file_without_sample, x, y, z)

        count_tallies = 0
        for tally in tallies:
            if tally.x == x and tally.y == y and tally.z == z:
                count_tallies += 1
                kk = tally.values.keys()
                kk.sort()
                kk = sorted(kk)
                #print [x[0] for x in kk]
                for en_diap in kk:
                    outt.write(str(tally_distance) + ',' + str(en_diap[0]) + ',' + str(en_diap[1]) + ',' + str(tally.values[en_diap]) + ',' + str(tally.dispersion[en_diap]) + '\n')
                    if en_diap[0] > 7:
                        continue
                    if mode == 'PP':
                        if en_diap[0] > 2:
                            continue
                    left.append(en_diap[0])
                    width.append(en_diap[1] - en_diap[0])

                    values.append((tally.values[en_diap] - etalon.values[en_diap]) * (en_diap[1] - en_diap[0]) / 4)

                    dy.append(tally.dispersion[en_diap]*values[-1]  * (en_diap[1] - en_diap[0]))
                    mid.append((en_diap[1] + en_diap[0])/2)
        if count_tallies == 0:
            print "Warning! No tallies for distance {len} found".format(len=tally_distance)
        plt.bar(left, values,width, color=col, yerr=dy, log=True, bottom=0.000000001, label=('distance to detector = ' + str(tally_distance) + 'cm.'))
        #plt.errorbar(left, values, color=col, yerr=dy, label=('distance to detector = ' + str(tally_distance) + 'cm.'))
        #plt.yscale('log')
        #plt.ylim([10**(-11),10**(-6)])
        plt.title(r'back flow.spectrum.\\sample len = ' + str(sample_length) + r'cm. mode = ' + mode)
        plt.xlabel(r'Energy, MEV')
        plt.ylabel(r'particles, $\bf \frac{F}{cm^2 sec MEV}$')

    outt.close()
    plt.legend()
    plt.grid()
    #plt.xscale('log')
    plt.savefig(pjoin(folder_to_place_images,title + ".png"), dpi = 300)
    print pjoin(folder_to_place_images,title + ".png")
    plt.show()
    plt.close()
    return left, values, width

def plot_sum_en_spectrum_in_back_going_flow(file_names, tally_distances, colors, files_without_sample, folder_to_place_images):
    neutron_file, photon_file = file_names
    etalon_n_file, etalon_p_file = files_without_sample
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
        x = 0
        y = 0
        z = 100 - tally_distance - 1.5
        etalon_n = construct_initial_spectrum_tally(etalon_n_file,x,y,z)
        etalon_p = construct_initial_spectrum_tally(etalon_p_file,x,y,z)
        for tally_ind, tally in enumerate(tallies_n):
            if tallies_n[tally_ind].x == x and tallies_n[tally_ind].y == y and tallies_n[tally_ind].z == z:
                if tallies_p[tally_ind].x != x or tallies_p[tally_ind].y != y or tallies_p[tally_ind].z != z:
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
                    values.append((tallies_n[tally_ind].values[en_diap] - etalon_n.values[en_diap] +
                                       (tallies_p[tally_ind].values[en_diap] - etalon_p.values[en_diap])/4)
                                        * (en_diap[1] - en_diap[0]))
                    temp = (tallies_n[tally_ind].dispersion[en_diap]*(tallies_n[tally_ind].values[en_diap] - etalon_n.values[en_diap]) + tallies_p[tally_ind].dispersion[en_diap]*(tallies_p[tally_ind].values[en_diap] - etalon_p.values[en_diap])/4 ) * (en_diap[1] - en_diap[0])
                    dy.append(min(temp, values[-1]))
                    mid.append((en_diap[1] + en_diap[0])/2)
        plt.bar(left, values,width, color=col, yerr=dy, log=True, bottom=0.000000001, label=('distance to detector = ' + str(tally_distance) + 'cm.'))
        #plt.errorbar(left, values, color=col, yerr=dy, label=('distance to detector = ' + str(tally_distance) + 'cm.'))
        #plt.yscale('log')
        #plt.ylim([10**(-11),10**(-6)])
        plt.title(r'back flow.spectrum.\\sample len = ' + str(sample_length) + r'cm. mode = full')
        plt.xlabel(r'Energy, MEV')
        plt.ylabel(r'particles, $\bf \frac{F}{cm^2 sec MEV}$')
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
    return left, values, width

def plot_dose_in_back_going_flow_for_each_file(names, tally_distanses, file_without_sample, folder_to_place_images):
    plt.figure(figsize=FIGURES_SIZE)
    legend = []
    for file_name in names:
        sample_length, mode = sample_length_and_mode_by_file_name(file_name)
        tallies = obr.construct_tallies(file_name)
        dosa_at_length = {}
        for tally_ind, tally in enumerate(tallies):
            if tally.x == 0 and tally.y == 0 and (100 - tally.z - 1.5 in tally_distanses):
                etalon = construct_initial_spectrum_tally(file_without_sample,
                                                          tally.x,
                                                          tally.y,
                                                          tally.z)
                dosa, dispersion = (tally.get_dose() - etalon.get_dose())
                if mode == 'PP':
                    dosa = dosa/4.
                dosa_at_length[100 - tally.z - 1.5] = (dosa, dispersion)
        x = sorted(dosa_at_length.keys())
        y = [dosa_at_length[k][0] for k in x]
        dy = [dosa_at_length[k][0]*dosa_at_length[k][1] for k in x]
        plt.yscale('log')
        plt.errorbar(x,y,yerr=dy)
        plt.xlabel('Distance to detector, sm.')
        plt.ylabel(r'Dose $\bf \frac{mkr}{sec}$')
        plt.grid('on')
        legend.append("Sample length = " + str(sample_length))
    title = "Dose in back going flow. mode = " + mode
    plt.title(title)
    plt.legend(legend, loc='best', prop={'size':LEGENDS_SIZE})
    plt.savefig(pjoin(folder_to_place_images,title + ".png"), dpi = 300)
    plt.show()

def plot_full_dose_in_back_going_flow_for_each_file(names, tally_distanses, files_without_sample, folder_to_place_images):
    plt.figure(figsize=FIGURES_SIZE)
    legend = []
    etalon_n_file, etalon_p_file = files_without_sample
    for neutron_file, photon_file in names:
        sample_length, garbage = sample_length_and_mode_by_file_name(neutron_file)
        tallies_n, tallies_p = obr.construct_tallies(neutron_file), obr.construct_tallies(photon_file)
        dosa_at_length = {}
        for tally_ind, (tally_n, tally_p) in enumerate(zip(tallies_n, tallies_p)):
            if tally_n.x == 0 and tally_n.y == 0 and (100 - tally_n.z - 1.5 in tally_distanses):
                etalon_n = construct_initial_spectrum_tally(etalon_n_file,
                                                              tally_p.x,
                                                              tally_p.y,
                                                              tally_p.z)
                etalon_p = construct_initial_spectrum_tally(etalon_p_file,
                                                              tally_p.x,
                                                              tally_p.y,
                                                              tally_p.z)
                dosa, dispersion = tally_n.get_dose() - etalon_n.get_dose() + (tally_p.get_dose() - etalon_p.get_dose())/4.
                dosa_at_length[100 - tally_n.z - 1.5] = (dosa, dispersion)
        x = sorted(dosa_at_length.keys())
        y = [dosa_at_length[k][0] for k in x]
        dy = [dosa_at_length[k][0]*dosa_at_length[k][1] for k in x]
        plt.yscale('log')
        plt.errorbar(x,y,yerr=dy)
        plt.xlabel('Distance to detector, sm.')
        plt.ylabel(r'Dose $\bf \frac{mkr}{sec}$')
        plt.grid('on')
        legend.append("Sample length = " + str(sample_length))
    title = "Dose in back going flow. mode = full."
    plt.title(title)
    plt.legend(legend, loc='best', prop={'size':LEGENDS_SIZE})
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

def plot_dose_after_the_sample(names, FOLDER_TO_SAVE_IMAGES, subpl=None):
    counter = 1
    if subpl is not None:
        plt.figure(figsize=(FIGURES_SIZE[0]*subpl[1], FIGURES_SIZE[0]*subpl[0]))
    for neutron_file, photon_file in names:
        if subpl is not None:
            plt.subplot(subpl[0], subpl[1], counter)
        counter += 1
        sample_length, garbage = sample_length_and_mode_by_file_name(neutron_file)
        tallies_n, tallies_p = obr.construct_tallies(neutron_file), obr.construct_tallies(photon_file)
        xs = []
        ys = []
        doses = []
        for tally_n, tally_p in zip(tallies_n, tallies_p):
            assert tally_n.is_the_same(tally_p), "Tallies are not correspond to each other."
            if abs(tally_n.x) > 20 or abs(tally_n.y) > 20:
                continue
            dose = tally_n.get_dose()[0] + tally_p.get_dose()[0]/4.
            for x,y in extend_x_y(tally_n.x,tally_n.y):
                xs.append(x)
                ys.append(y)
                doses.append(dose)
        xis = np.linspace(-20,20,100)
        yis = np.linspace(-20,20,100)
        #zis = griddata(xs,ys,doses,xis,yis,interp='linear')
        zis = griddata(xs,ys,doses,xis,yis,interp='nn')
        CS = plt.contour(xis, yis, zis, 5, linewidths=0.5, colors='b')
        CS = plt.contourf(xis, yis, zis, 5, cmap=plt.cm.rainbow,
                  vmax=abs(zis).max(), vmin=-abs(zis).max())
        cbar = plt.colorbar()

        plt.scatter(xs,ys,c=doses, cmap=plt.cm.rainbow, vmax=abs(zis).max(), vmin=-abs(zis).max())#, s=norm(doses)*30000)
        plt.xlim(-21,21)
        plt.ylim(-21,21)
        cbar.set_label(r'$\frac{mkr}{sec}$')
        title = "Dose after the sample.\n sample length = " + str(sample_length) + '. mode = full'
        plt.title(title)
        plt.xlabel("'x' dimension, sm")
        plt.ylabel("'y' dimension, sm")
        if subpl is None:
            plt.savefig(pjoin(FOLDER_TO_SAVE_IMAGES, title + '.png'), dpi=300)
            plt.show()

    if subpl is not None:
        plt.savefig(pjoin(FOLDER_TO_SAVE_IMAGES, 'Doses_after_the_sample.' + '.png'), dpi=300)
