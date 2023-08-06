import logging
import statistics
import sys
import traceback
from logging.handlers import TimedRotatingFileHandler
from time import time, perf_counter_ns, sleep

import numpy

from kamzik3.snippets.snippetsTimer import PreciseCallbackTimer

base_log_formatter = logging.Formatter('%(asctime)s, %(name)s, %(levelname)s, %(message)s', datefmt='%Y-%m-%d %H:%M:%S')


def set_file_handler(logger, log_output_dir, formatter=base_log_formatter):
    handler = logging.FileHandler(log_output_dir)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return handler


def set_rotating_file_handler(logger, log_output_dir, formatter=base_log_formatter):
    handler = TimedRotatingFileHandler(log_output_dir, when="midnight")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return handler


def get_console_handler(log_level=logging.DEBUG, formatter=base_log_formatter):
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    return console_handler


def set_sys_exception_handler(logger):
    def handle_exception(exc_type, exc_value, exc_traceback):
        logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
        sys.__excepthook__(exc_type, exc_value, exc_traceback)

    sys.excepthook = handle_exception


def print_exception():
    print(traceback.format_exc())


class MeasureTiming:

    def __init__(self, title, timeout, save_file, measure_time=10000):
        self.spacing = []
        self.error = []
        self.title = title
        self.measure_time = int(measure_time)
        self.samples = 0
        self.running = False
        self.timeout = timeout
        self.timer = None
        self.save_file = save_file
        self.reference_time_perf = perf_counter_ns()

    def start_measurement(self):
        self.spacing = []
        self.error = []
        self.samples = 0
        self.running = True
        self.timer = PreciseCallbackTimer(self.measure_time + 10*self.timeout, self.plot)
        self.reference_time_perf = perf_counter_ns()
        self.timer.start()

    def measure(self):
        if not self.running:
            return
        t_diff = (perf_counter_ns() - self.reference_time_perf) * 1e-6
        self.reference_time_perf = perf_counter_ns()
        self.spacing.append(t_diff)
        self.error.append(abs(t_diff - self.timeout))
        self.samples += 1

    def plot(self):
        self.running = False
        self.timer.stop()
        sleep(0.5)
        self.spacing = self.spacing[5:-5]
        self.error = self.error[5:-5]
        print(self.title)
        print(time(), "Frequency:", self.samples, "Median:", statistics.median(self.spacing),
              "Mean:", statistics.mean(self.spacing), "Min:", min(self.spacing), "Max:", max(self.spacing), "Std:",
              numpy.std(self.spacing))
        print("Median error:", statistics.median(self.error), "Mean error:", statistics.mean(self.error), "Min:",
              min(self.error),
              "Max:",
              max(self.error),
              "Std:", numpy.std(self.error))

        import matplotlib.pyplot as plt
        plt.subplot(2, 1, 1)
        plt.scatter(range(len(self.spacing)), self.spacing, s=2, c="r")
        plt.title(self.title)
        plt.xlabel('samples [count]')
        plt.ylabel('spacing [ms]')

        plt.subplot(2, 1, 2)
        plt.scatter(range(len(self.error)), self.error, s=2, c="r")
        plt.xlabel('samples [count]')
        plt.ylabel('error [ms]')

        plt.savefig(self.save_file)
