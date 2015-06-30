__author__ = 'griddic'

import shutil
import os
from os.path import join as pjoin
from os.path import isfile
import time
import sys
import tempfile
import StringIO
import traceback


def sys_traceback():
    s = StringIO.StringIO()
    traceback.print_exception(*sys.exc_info(), file=s)
    return s.getvalue()


from macc_grabber import get_macc_file
from parameters_parser import get_parameters
from time_functions import stamp_Ymd, stamp_Y_m_d
from os_functions import module_path, verify_folder_existence
from os_functions import clean_folder, execute_to_writable
from time_functions import time_now
from run_any_location_forecast import place_wrfchemi_into_wrf_regular_dir


#### functions for logger
import logging
import logging.handlers
from threading import Thread
import smtplib


def smtp_at_your_own_leasure(mailhost, port, username, password, fromaddr, toaddrs, msg):
    smtp = smtplib.SMTP(mailhost, port)
    if username:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
        smtp.login(username, password)
    smtp.sendmail(fromaddr, toaddrs, msg)
    smtp.quit()


class TlsSMTPHandler(logging.handlers.SMTPHandler):
    def emit(self, record):
        try:
            import string

            try:
                from email.utils import formatdate
            except ImportError:
                formatdate = self.date_time
            port = self.mailport
            if not port:
                port = smtplib.SMTP_PORT
            msg = self.format(record)
            msg = "From: %s\r\nTo: %s\r\nSubject: %s\r\nDate: %s\r\n\r\n%s" % (
                self.fromaddr,
                string.join(self.toaddrs, ","),
                self.getSubject(record),
                formatdate(), msg)
            thread = Thread(target=smtp_at_your_own_leasure,
                            args=(self.mailhost, port, self.username, self.password, self.fromaddr, self.toaddrs, msg))
            thread.start()
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)
#### end functions for logging


def construct_out_file_name():
    return "wrf_chem_input_d01" + stamp_Ymd()


def cut_hour_from_forecast(forecast_file, hour, out_file, logger):
    with tempfile.NamedTemporaryFile() as temp_file:
        temp_file_name = os.path.abspath(temp_file.name)

    logger.debug('ncks -d Time,{t} "{name}" {tmp_file}'.format(t=hour, name=forecast_file, tmp_file=temp_file_name))
    os.system('ncks -d Time,{t} "{name}" {tmp_file}'.format(t=hour, name=forecast_file, tmp_file=temp_file_name))
    logger.debug('Move {tmp_file} into {location}.'.format(tmp_file=temp_file_name, location=out_file))
    if os.path.isfile(out_file):
        os.remove(out_file)
    os.rename(temp_file_name, out_file)


def compute_initial_approximation(folder_to_place_new_wrf_input, logger):
    """
    Compute initial approximation for father calculations.
    """
    logger.debug('go into ' + module_path())
    os.chdir(module_path())
    out_file_name = construct_out_file_name()

    if isfile(out_file_name):
        shutil.copy(out_file_name, pjoin(folder_to_place_new_wrf_input, 'wrf_chem_input_d01_' + stamp_Ymd()))
        logger.debug("File {outt} is already on the disk.".format(outt=out_file_name))
        func_out = StringIO.StringIO()
        execute_to_writable('clean_folder(folder_to_place_new_wrf_input, lambda x: True, 7)',
                            func_out, globals(), locals())
        logger.debug(func_out.getvalue())
        return True
    p = get_parameters('parameters.csv', 'PREPROCESSING')

    ####################################### place wrfchemi into wrf regular directory ##################################
    place_wrfchemi_into_wrf_regular_dir(pjoin('templates', 'PP_wrfchemi_d01.template'), p.WRF_REGULAR_DIR, days_shift=1)
    logger.debug('wrfchemi created')

    while True:
        try:
            macc_file = get_macc_file()
            break
        except:
            if time_now().hour > 6:
                raise Exception("Can't download MACC file.")
            else:
                logger.debug("Can't download MACC file.")
                logger.debug("Waiting {0} seconds for another attempt.".format(5 * 60))
                time.sleep(5 * 60)

    if isfile(pjoin(p.WRF_REGULAR_DIR, 'wrf_chem_input_d01')):
        os.remove(pjoin(p.WRF_REGULAR_DIR, 'wrf_chem_input_d01'))
        logger.debug("Old wrf_chem_input_d01 was deleted.")

    logger.debug('python macc2wrf_input.py -m ' + macc_file +
                 ' -t ' + pjoin('macc', 'wrf_chem_input_d01.template') +
                 ' -o ' + pjoin(p.WRF_REGULAR_DIR, 'wrf_chem_input_d01'))
    os.system('python macc2wrf_input.py -m ' + macc_file +
              ' -t ' + pjoin('macc', 'wrf_chem_input_d01.template') +
              ' -o ' + pjoin(p.WRF_REGULAR_DIR, 'wrf_chem_input_d01'))

    logger.debug('preprocessing start at {0}'.format(time_now()))
    os.system('python run_any_location_forecast.py -m PREPROCESSING')
    logger.debug('preprocessing done at {0}'.format(time_now()))
    verify_folder_existence(folder_to_place_new_wrf_input)
    forecasts = [x for x in os.listdir(p.WRF_OUT_DIR) if x.startswith('forecast')]
    forecasts = [x for x in forecasts if x.find(stamp_Y_m_d(shift_days=1)) != -1]
    forecast = sorted(forecasts)[0]
    forecast = pjoin(p.WRF_OUT_DIR, forecast)
    for hour in [0, 6, 12, 18]:
        cut_hour_from_forecast(forecast,
                               hour + 24,
                               pjoin(folder_to_place_new_wrf_input,
                                     'wrf_chem_input_d01_{ymd}{h}'.format(ymd=stamp_Ymd(), h=str(hour).rjust(2, '0'))),
                               logger)

    logger.debug(
        "Result placed in {0}.".format(pjoin(folder_to_place_new_wrf_input, 'wrf_chem_input_d01_' + stamp_Ymd())))


if __name__ == '__main__':

    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger()
    print "Logging to: ", os.path.join(os.path.split(__file__)[0],
                                       'logs',
                                       'initial_approximation.log')
    if not os.path.isdir(os.path.join(os.path.split(__file__)[0], 'logs')):
        os.makedirs(os.path.join(os.path.split(__file__)[0], 'logs'))
    log_file = logging.handlers.RotatingFileHandler(os.path.join(os.path.split(__file__)[0],
                                                                 'logs',
                                                                 'initial_approximation.log'),
                                                    maxBytes=2000000, backupCount=5)
    log_file.setLevel(logging.DEBUG)
    log_file.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(log_file)

    mail_handler = TlsSMTPHandler(mailhost=('smtp.yandex.ru', 25),
                                  fromaddr="",
                                  toaddrs="",
                                  subject=u"!!! Computing initial approximation error !!!",
                                  credentials=('',
                                               ''))
    mail_handler.setLevel(logging.ERROR)
    mail_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

    logger.addHandler(mail_handler)

    logger.debug("Computing initial approximation is started.")

    pid = os.getpid()
    logger.debug("Process PID is {pid}".format(pid=pid))
    pid_file_name = os.path.abspath(__file__) + '.pid'
    with open(pid_file_name, 'a') as pid_file:
        print >> pid_file, pid, ' '.join(sys.argv), '; started at ', time_now()

    def remove_pid_from_file():
        with open(pid_file_name) as pid_file:
            lines = pid_file.readlines()
        new_lines = []
        for line in lines:
            line = line.strip()
            if len(line) == 0:
                continue
            if line.split()[0] == str(pid):
                continue
            new_lines.append(line)
        os.remove(pid_file_name)
        with open(pid_file_name, 'w') as pid_file:
            for line in new_lines:
                print >> pid_file, line

    try:
        compute_initial_approximation('/home/wrf/data/wrf_chem_input_storage/', logger)
    except:
        logger.fatal(sys_traceback())
    func_out = StringIO.StringIO()
    execute_to_writable('clean_folder("/home/wrf/data/wrf_chem_input_storage/", lambda x: True, 7)',
                        func_out)
    logger.debug(func_out.getvalue())

    remove_pid_from_file()
