import logging
import sys

__all__ = ['gxlogger']


class gxlogger(object):
    def __init__(self):
        self.formatter = logging.Formatter('[%(levelname)s] %(asctime)s %(funcName)s{%(lineno)d}:%(message)s',
                                           datefmt='%Y-%m-%d %I:%M:%S %p')
        ch = logging.StreamHandler(sys.stdout)
        ch.setFormatter(self.formatter)
        self.shared = logging.getLogger('gxlogger')
        self.shared.addHandler(ch)
        self.shared.setLevel(logging.DEBUG)

    def setFormatter(self, f):
        self.formatter = f

    def logger(self):
        return self.shared

