# This file is placed in the Public Domain.
#
# pylint: disable=C,I,R
# pylama: ignore=E402,E302,E265


"inheritence"


__author__ = "Bart Thate <programmingobject@gmail.com>"


import unittest


from opr import Object


class A(Object):

    pass

class B(Object):

    pass


class C(A, B):

    bla = "mekker"


class D:

    pass


class E(A, D):

    pass


class F(C, D):

    pass


class H(dict):

    pass


class TestInherit(unittest.TestCase):

    def testbare(self):
        d = D()
        self.assertEqual(type(d), D)

    def testObjectObject(self):
        c = C()
        self.assertEqual(type(c), C)

    def testObjectbare(self):
        e = E()
        self.assertEqual(type(e), E)

    def testinheritObjectObjectbare(self):
        f = F()
        self.assertEqual(type(f), F)

    def testobjectobjectbarecontent(self):
        f = F()
        self.assertEqual(f.bla, "mekker")

    def testdict(self):
        h = H()
        self.assertEqual(type(h), H)

    def testobject(self):
        class I(object):
            pass
        i = I()
        self.assertEqual(type(i), I)

    def testobjectobject(self):
        class I(object):
            pass
        class J(A, I):
            pass
        j = J()
        self.assertEqual(type(j), J)

    def testobjectObjectObjectobject(self):
        class I(object):
            pass
        class J(A, I):
            pass
        class K(J, H):
            pass
        k = K()
        self.assertEqual(type(k), K)

    def testaggregate(self):
        def check():
            class I(object):
                pass
            class J(A, I):
                pass
            class K(J, H):
                pass
            k = K()
            k["a"] = "b"
        with self.assertRaises(TypeError):
            check()
