# This file is placed in the Public Domain.


"""clock"""


# IMPORTS


import threading
import time


from opr.objects import Object
from opr.threads import Thread, launch


# INTERFACE


def __dir__():
    return (
            'Repeater',
            'Timer',
            'elapsed'
           )


__all__ = __dir__()


# CLASSES


class Timer:

    """run x seconds from now"""

    def __init__(self, sleep, func, *args, thrname=None):
        super().__init__()
        self.args = args
        self.func = func
        self.sleep = sleep
        self.name = thrname or str(self.func).split()[2]
        self.state = Object
        self.timer = None

    def run(self) -> None:
        """launch function in its thread"""
        self.state.latest = time.time()
        launch(self.func, *self.args)

    def start(self) -> None:
        """start waiting till its time"""
        timer = threading.Timer(self.sleep, self.run)
        timer.name = self.name
        timer.daemon = True
        timer.sleep = self.sleep
        timer.state = self.state
        timer.state.starttime = time.time()
        timer.state.latest = time.time()
        timer.func = self.func
        timer.start()
        self.timer = timer

    def stop(self) -> None:
        """stop waiting"""
        if self.timer:
            self.timer.cancel()


class Repeater(Timer):

    """run function every x seconds"""

    def run(self) -> Thread:
        thr = launch(self.start)
        super().run()
        return thr


# UTILITY


def elapsed(seconds, short=True) -> str:
    "return elapsed time string"
    txt = ""
    nsec = float(seconds)
    if nsec < 1:
        return f"{nsec:.2f}s"
    year = 365*24*60*60
    week = 7*24*60*60
    nday = 24*60*60
    hour = 60*60
    minute = 60
    years = int(nsec/year)
    nsec -= years*year
    weeks = int(nsec/week)
    nsec -= weeks*week
    nrdays = int(nsec/nday)
    nsec -= nrdays*nday
    hours = int(nsec/hour)
    nsec -= hours*hour
    minutes = int(nsec/minute)
    nsec -= int(minute*minutes)
    sec = int(nsec)
    if years:
        txt += f"{years}y"
    if weeks:
        nrdays += weeks * 7
    if nrdays:
        txt += f"{nrdays}d"
    if years and short and txt:
        return txt.strip()
    if hours:
        txt += f"{hours}h"
    if minutes:
        txt += f"{minutes}m"
    if sec:
        txt += f"{sec}s"
    txt = txt.strip()
    return txt
