__author__ = 'griddic-work'

import os
from os.path import join as pjoin
import sys
import time
from datetime import datetime, timedelta
import shutil
from copy import deepcopy


def time_now(shift_hours=0):
    """Return GMT rounded to seconds.
    """
    return datetime.now() + timedelta(hours=shift_hours)


def is_older(file_, time_, delta=200000):
    file_time = datetime.fromtimestamp(os.path.getctime(file_))
    if (time_ - file_time).total_seconds() > delta:
        return True
    return False


def verify_folder_existence(folder):
    """ if folder isn't exist, this function crate it.
    """
    if not os.path.exists(folder):
        os.makedirs(folder)


def we_are_frozen():
    # All of the modules are built-in to the interpreter, e.g., by py2exe
    return hasattr(sys, "frozen")


def module_path():
    encoding = sys.getfilesystemencoding()
    if we_are_frozen():
        return os.path.dirname(unicode(sys.executable, encoding))
    return os.path.abspath(os.path.dirname(unicode(__file__)))


def check_pid(pid):
    """ Check For the existence of a unix pid. """
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    else:
        return True


def check_pid_from_file(file_):
    if not os.path.isfile(file_):
        return None, None
    with open(file_) as inn:
        try:
            pid = int(inn.read().strip())
        except:
            assert False, 'Not a PID.'
    return check_pid(pid), pid


def remove(file_):
    if os.path.isfile(file_):
        os.remove(file_)


class McnpRun:
    def __init__(self, file_name):
        self.in_file = os.path.split(file_name)[1]
        shutil.copy(file_name, self.in_file)
        self.out_file = self.in_file + 'a'
        self.log_file = self.in_file + '.log'
        self.pid_file = self.in_file + '.pid'
        self.command = 'nohup mcnpx I={inn} o={outt} > {log} 2>&1 & echo $! > {pid}'.format(inn=self.in_file,
                                                                                            outt=self.out_file,
                                                                                            log=self.log_file,
                                                                                            pid=self.pid_file)
        self.run_time = time_now()

    def run(self):
        is_run, pid = check_pid_from_file(self.pid_file)
        if is_run is not None:
            if is_run:
                os.system('kill ' + str(pid))
        remove(self.out_file)
        os.system(self.command)

    def is_ready(self):
        is_run, pid = check_pid_from_file(self.pid_file)
        if is_run is None:
            assert False, 'PID file not found for' + self.in_file
        if is_run:
            return False
        with open(self.log_file) as inn:
            success = inn.readlines()[-1].find('done') != -1
        if success:
            return True
        print self.in_file, ' not success run. Restarting.'
        self.run()
        return False

    def place_results_to_fold_and_clean_up(self, folder):
        shutil.move(self.out_file, pjoin(folder, self.out_file))
        shutil.move(self.log_file, pjoin(folder, self.log_file))
        remove(self.in_file)


def main():
    log_file = os.path.abspath(__file__) + '.log'
    log = open(log_file, mode='a', buffering=0)
    sys.stdout = log
    print '=' * 80
    os.chdir(module_path())
    mcnp_input_folder = os.path.abspath('mcnp_input')
    verify_folder_existence('mcnp_out')
    mcnp_output_folder = os.path.abspath('mcnp_out')
    verify_folder_existence('mcnp_process_4_1')
    os.chdir('mcnp_process_4_1')
    mcnp_runs = set()
    names_local = ['NN0', 'NN10', 'NN15', 'NN20', 'NN25', 'NN30', 'NN35', 'NN40', 'NN45', 'NN5', 'NN50',
                   'NP0', 'NP10', 'NP15', 'NP20', 'NP25', 'NP30', 'NP35', 'NP40', 'NP45', 'NP5', 'NP50',
                   'PP0', 'PP10', 'PP15', 'PP20', 'PP25', 'PP30', 'PP35', 'PP40', 'PP45', 'PP5', 'PP50']
    names = []
    for name in names_local:
        names.append(pjoin(mcnp_input_folder, name))
    i = 0
    counter = 0
    while True:
        if counter < 99:
            sys.stdout.write('.')
        else:
            print '.'
            sys.stdout.write(' '.join([x.in_file for x in mcnp_runs]))
            counter = 0
        counter += 1

        if i < len(names):
            if len(mcnp_runs) < 4:
                print time_now(), ": Start dealing with", names[i]
                new_run = McnpRun(names[i])
                i += 1
                new_run.run()
                mcnp_runs.add(new_run)
        else:
            if len(mcnp_runs) == 0:
                break
        oldest_run_time = time_now()
        actual_mcnp_runs = set()
        for run in mcnp_runs:
            if run.run_time < oldest_run_time:
                oldest_run_time = run.run_time
            if run.is_ready():
                run.place_results_to_fold_and_clean_up(mcnp_output_folder)
                print time_now(), ": end dealing with", run.in_file
                print "#" * 80
                print run.in_file, ' was computed by ', time_now() - run.run_time
                print "#" * 80
                #mcnp_runs.remove(run)
            else:
                actual_mcnp_runs.add(run)
        mcnp_runs = deepcopy(actual_mcnp_runs)

        runtpes = os.listdir(os.curdir)
        runtpes = [x for x in runtpes if x.startswith('runtp')]
        runtpes_to_delete = [x for x in runtpes if is_older(x, oldest_run_time)]
        for file_ in runtpes_to_delete:
            os.remove(file_)
        time.sleep(60)


if __name__ == '__main__':
    main()