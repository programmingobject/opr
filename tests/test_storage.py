# This file is placed in the Public Domain.
#
# pylint: disable=C0114,C0115,C0116,W0703,C0413,R0801
# pylama: ignore=E402


import os
import unittest


from opr.objects import Object
from opr.persist import Persist, write


from opr import persist


Persist.workdir = '.test'


ATTRS1 = ('Persist',
          'files',
          'find',
          'fnclass',
          'fns',
          'fntime',
          'hook',
          'last',
          'read',
          'readrec',
          'search',
          'write',
          'writerec'
         )


class TestStorage(unittest.TestCase):

    def test_constructor(self):
        obj = Persist()
        self.assertTrue(type(obj), Persist)

    def test__class(self):
        obj = Persist()
        clz = obj.__class__()
        self.assertTrue('Persist' in str(type(clz)))

    def test_dirmodule(self):
        self.assertEqual(
                         dir(persist),
                         list(ATTRS1)
                        )

    def test_module(self):
        self.assertTrue(Persist().__module__, 'persist')

    def test_save(self):
        Persist.workdir = '.test'
        obj = Object()
        opath = write(obj)
        self.assertTrue(os.path.exists(Persist.path(opath)))
