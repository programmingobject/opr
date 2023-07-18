# This file is placed in the Public Domain.


"test imports"


__author__ = "Bart Thate <programmingobject@gmail.com>"


import sys


NAME = __name__.split('.', maxsplit=1)[0]
sys.path.insert(0, NAME)
