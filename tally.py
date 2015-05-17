# -*- coding: utf-8 -*-
# __author__ = 'griddic'
from collections import defaultdict
import numpy as np


class Tally:
    shneider_function_coefficients = [-6.72023666e-05,
                                      6.47731559e-04,
                                      -1.13328468e-04,
                                      1.38962184e-05,
                                      -6.03541123e-07]
    def shneider_function(self, x_arr):
        ans = np.zeros(len(x_arr))
        for power, multiplier in enumerate(self.shneider_function_coefficients):
            ans += np.power(x_arr, power)*multiplier
        return ans


    def __init__(self, particle_type, x, y, z, lx, ly, lz):
        self.particle_type = particle_type
        self.x = x
        self.y = y
        self.z = z
        self.lx = lx
        self.ly = ly
        self.lz = lz
        self.values = defaultdict(float)
        self.dispersion = defaultdict(float)

    def is_the_same(self, other_tally):
        if self.particle_type != other_tally.particle_type:
            return False
        if self.x != other_tally.x:
            return False
        if self.y != other_tally.y:
            return False
        if self.z != other_tally.z:
            return False
        if self.lx != other_tally.lx:
            return False
        if self.ly != other_tally.ly:
            return False
        if self.lz != other_tally.lz:
            return False
        return True

    def feed(self, data_lines, cell_name):
        begin = -1
        for i in range(len(data_lines)):
            if len(data_lines[i].split()) > 1 and data_lines[i].split()[0] == "cell" and data_lines[i].split()[1] == cell_name:
                begin = i + 2
                break
        if begin == -1:
            raise NameError, "wrong cell_name = " + cell_name
        end = -1
        for i in range(begin, len(data_lines)):
            if data_lines[i].strip().split()[0] == "total":
                end = i
                break

        previous_energy = float(0)
        for i in range(begin, end):
            line = data_lines[i].strip().split()
            self.add_value_from_energy_diaposon((previous_energy, float(line[0])),
                                                float(line[1]), float(line[2]))
            previous_energy = float(line[0])
        pass

    def add_value_from_energy_diaposon(self, diaposon, value, dispersion):
        self.values[diaposon] += value
        if value + self.values[diaposon] == 0:
            self.dispersion[diaposon] = 0
        else:
            self.dispersion[diaposon] = (self.dispersion[diaposon]*self.values[diaposon] + value*dispersion)/(value + self.values[diaposon])

    def get_value_from_diaposon(self, minE=0, maxE=100):
        minE = float(minE)
        answer = 0
        disp = 0
        for key in self.values.keys():
            if minE <= key[0] and maxE > key[1]:
                answer += self.values[key]
                if (self.values[key] + answer) == 0:
                    disp = 0
                else:
                    disp = (self.values[key]*self.dispersion[key] + answer*disp)/(self.values[key] + answer)
        return answer, disp

    def get_dose(self):
        u"""  Возвращает дозу в мкр/сек.
        """
        keys_ = sorted(self.values.keys())
        energies = np.array([(x[0]+x[1])/2. for x in keys_])
        values = np.array([self.values[k] for k in keys_])
        dispersion = np.array([self.dispersion[k] for k in keys_])
        abs_errors = values*dispersion

        shneider_multipliers = self.shneider_function(energies)
        dosa = np.sum(values * shneider_multipliers)
        abs_err = np.sum(dispersion * shneider_multipliers)
        return np.array([dosa, abs_err])