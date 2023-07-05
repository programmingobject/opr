# This file is placed in the Public Domain.
#
# pylint: disable=C0413,C0115,C0116,E1101
# pylama: ignore=W0611,E303,E402


"""
    >>> import opr.objects as opr
    >>> o = opr.Object()
    >>> o.o = opr.Object()
    >>> o.o.a = "test"
    >>> print(o)
    {'o': {'a': 'test'}}

"""


import unittest


from opr.objects import Object
from opr.persist import readrec, writerec


class TestRecursive(unittest.TestCase):

    def testrecursive(self):
        obj = Object()
        obj.obj = Object()
        obj.obj.a = "test"
        pth = writerec(obj)
        print(pth)
        readrec(obj, pth)
        self.assertEqual(obj.obj.a, "test")
