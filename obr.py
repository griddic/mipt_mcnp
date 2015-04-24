# -*- coding: utf-8 -*-
u""" для геометрии состоящей только из прямоуголных объектов
 собирает информацию и генерирует графики. """
__author__ = 'GRIDDIC'

import optparse
from collections import defaultdict
from copy import copy, deepcopy

from tally import Tally

def get_task_parameters(file_name):
    u""" обрабатывает сгенерированный MCNP файл,
    возвращает тип испускаемых частиц, на какие частицы был настроен приёмник,
    длинну образца и количетво сгенерированных MCNP частиц.
    Для корректной работы необходимо, чтобы образец был описан макрофигурой RPP,
    c комментарием 'sample'"""
    with open(file_name) as inn:
        data = inn.read()
    with open(file_name) as inn:
        data_lines = inn.readlines()
    source_type = data[data.find("PAR", data.find("SDEF")) + 4]
    if source_type == '1':
        source_particles = "neutrons"
    if source_type == '2':
        source_particles = "photons"

    tally_type = data[data.find(":",data.find("F", data.find("SDEF") + 5)) + 1]
    if tally_type == 'N':
        tally_particles = "neutrons"
    if tally_type == 'P':
        tally_particles = "photons"

    sample_len = -1
    for line in data_lines:
        if line.find("sample") == -1:
            continue
        if line.find("RPP") == -1:
            continue

        sample_len = int(line.split()[8]) - int(line.split()[7])
        break

    nps = int(data[data.find('nps') + 4: data.find('\n', data.find("nps"))].strip())

    return source_particles, tally_particles, sample_len, nps

def read_description(in_file):
    """ from MCNPout file extract MCNPin file
    return lines"""
    lines = []
    with open(in_file) as inn:
        data_lines = inn.readlines()
    in_description = False
    for line in data_lines:
        if len(line.strip().split()) > 0 and line.strip().split()[0] == '1-':
            in_description = True
        if not in_description:
            continue
        if len(line.strip()) == 0:
            break
        if line.strip().split()[0] == 'warning.':
            continue
        lines.append(line[13:].rstrip())
    lines_joined = []
    for line in lines:
        if len(line) > 6 and line[:5] == "     ":
            lines_joined[-1] += (" " + line.rstrip())
            continue
        lines_joined.append(line)
    return lines_joined

def get_geometry_and_primitives(lines):
    #lines = read_description(file_name)
    index = 1
    geometry = []
    while len(lines[index]) != 0:
        geometry.append(lines[index])
        index += 1

    primitives = []
    index += 1
    while len(lines[index]) != 0:
        primitives.append(lines[index])
        index += 1


    geometry_dict = {}
    for geo in geometry:
        k, v = parse_description_geometry_line(geo)
        geometry_dict[k] = v

    primitives_dict = {}
    for geo in primitives:
        k, v = parse_description_primitives_line(geo)
        primitives_dict[k] = v

    return geometry_dict, primitives_dict


def parse_description_line(line, should_copy=True):
    if line.find('$') != -1:
        line = line[:line.find('$')]
    line = line.replace("imp:N=1","")
    line = line.replace("imp:P=1","")
    line = line.replace("imp:N 1","")
    line = line.replace("imp:P 1","")
    line = line.replace("imp:N=0","")
    line = line.replace("imp:P=0","")
    line = line.replace("imp:N 0","")
    line = line.replace("imp:P 0","")
    return line

def parse_description_geometry_line(line_):
    line = parse_description_line(line_)
    line = line.strip().split()
    if line[1] == '0':
        return line[0], line[2:]
    else:
        return line[0], line[3:]

def parse_description_primitives_line(line_):
    line = parse_description_line(line_)
    line = line.strip().split()
    return line[0], line[1:]

def get_tallies(lines):
    for line in lines:
        if len(line) > 0 and line[0] == "F":
            return line.split()[1:]




def construct_tallies(file_name):
    with open(file_name) as inn:
        data_lines = inn.readlines()
    description = read_description(file_name)
    tallies = []
    particles_type = get_task_parameters(file_name)[1]
    tallies_names = get_tallies(description)
    #print tallies_names
    geometry , primitives = get_geometry_and_primitives(description)
    for tally_name in tallies_names:
        p = [float(x) for x in primitives[str(abs(int(geometry[tally_name][0])))][1:]]
        #print p
        x = (p[1] + p[0])/2
        y = (p[2] + p[3])/2
        z = (p[4] + p[5])/2
        lx = p[1] - p[0]
        ly = p[3] - p[2]
        lz = p[5] - p[4]
        tallies.append(Tally(particles_type, x, y, z, lx, ly, lz))
    for i in range(len(tallies_names)):
        tallies[i].feed(data_lines, tallies_names[i])
    return tallies

def main():
    tellies = construct_tallies("PN10a")
    print len(tellies)
    pp = []
    for telly in tellies:
        if telly.y < 100:
            pp.append(telly.z)
    pp.sort()
    print pp
    pass


if __name__ == "__main__":
    main()