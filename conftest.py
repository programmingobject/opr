# This file is placed in the Public Domain.
#
# pylint: disable=C,I,R


"configure tests"


__author__ = "Bart Thate <programmingobject@gmail.com>"


def pytest_sessionfinish(session, exitstatus):
    if exitstatus == 5:
        session.exitstatus = 0 # Any arbitrary custom status you want to return```
        