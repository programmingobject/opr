# This file is placed in the Public Domain.
#
# pylint: disable=C,I,R


"interface"


import logging
import sys
import unittest


from opr.objects import Object, get


METHODS = [
           'clear',
           'copy',
           'fromkeys',
           'get',
           'items',
           'keys',
           'pop',
           'popitem',
           'setdefault',
           'update',
           'values'
          ]


class A(Object):

    def a(self):
        return "b"


DICT = {}

DIFF = [
        '__default__',
        '__dict__',
        '__getattr__',
        '__module__',
        '__oid__',
        '__slots__',
        '__test__',
        '_pytestfixturefunction'
       ]
DIFF = [
        '__dict__',
        '__module__',
        '__oid__',
        '__slots__'
       ]
OBJECT = Object()


class TestInterface(unittest.TestCase):

    def test_interface(self):
        dictkeys = dir(DICT)
        objectkeys = dir(OBJECT)
        res = []
        for key in objectkeys:
            if key not in dictkeys:
                res.append(key)
        self.assertEqual(res, DIFF)

    def test_methodinterface(self):
        okd = True
        for meth in METHODS:
            func1 = get(OBJECT, meth)
            if not func1:
                continue
            func2 = DICT.get(meth)
            if not func2:
                continue
            if dir(func1) != dir(func2):
                print(func1, func2)
                okd = False
            sys.stdout.flush()
        self.assertTrue(okd)


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stderr)
    logging.getLogger("SomeTest.testSomething").setLevel(logging.DEBUG)
    unittest.main()
