# This file is placed in the Public Domain.


"configure tests"


__author__ = "Bart Thate <programmingobject@gmail.com>"


def pytest_sessionfinish(session, exitstatus):
    if exitstatus == 5:
        session.exitstatus = 10 # Any arbitrary custom status you want to return```
        