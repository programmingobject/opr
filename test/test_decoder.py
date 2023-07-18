# This file is placed in the Public Domain.
#
# pylint: disable=C0114,C0115,C0116,W0703,C0413
# pylama: ignore=E402


"decoding objects"


__author__ = "Bart Thate <programmingobject@gmail.com>"


import unittest


from opr import Object, loads, dumps


class TestDecoder(unittest.TestCase):

    def test_loads(self):
        obj = Object()
        obj.test = "bla"
        oobj = loads(dumps(obj))
        self.assertEqual(oobj.test, "bla")
