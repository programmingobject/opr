# This file is placed in the Public Domain.
#
# pylint: disable=C0114,C0115,C0116,W0703,C0413
# pylama: ignore=E402


import unittest


from opr.handler import parse
from opr.objects import Object


class TestDecoder(unittest.TestCase):

    def test_parse(self):
        prs = Object()
        parse(prs, "cmd")
        self.assertEqual(prs["cmd"], "cmd")
