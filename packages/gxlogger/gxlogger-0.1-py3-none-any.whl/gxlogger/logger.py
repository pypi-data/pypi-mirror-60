import logging

__all__ = ['gxlogger']


class gxlogger(object):
    def __init__(self):
        self.formatter = logging.Formatter('[%(levelname)s] %(asctime)s %(funcName)s{%(lineno)d}:%(message)s',
                                           datefmt='%Y-%m-%d %I:%M:%S %p')
        self.shared = logging.getLogger('gxlogger')
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        # add formatter to ch
        ch.setFormatter(self.formatter)
        self.shared.addHandler(ch)

    def setFormatter(self, f):
        self.formatter = f

    def logger(self):
        return self.shared

