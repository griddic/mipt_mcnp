__author__ = 'griddic'

import os
import sys
from datetime import datetime

from time_functions import time_now


def check_pid(pid):
    """ Check For the existence of a unix pid. """
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    else:
        return True

def change_dir(folder):
    """ The same as os.chdir(), but verify folder existence before.
    """

def verify_path_existence(path):
    """ path - is a FILE path, not the sequence!
     if path to the file isn't exist, this function crate it.
    """
    verify_folder_existence(os.path.dirname(path))

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


def last_string(file_name):
    return [x.strip() for x in open(file_name).readlines() if len(x.strip()) != 0][-1]


def last_strings(file_name, quantity_of_strings):
    lines = [x.strip() for x in open(file_name).readlines() if len(x.strip()) != 0]
    return '\n'.join(lines[max(len(lines) - quantity_of_strings, 0):])


def file_age_in_days(file_name):
    return (time_now() - datetime.fromtimestamp(os.path.getctime(file_name))).days

