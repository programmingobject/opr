# This file is placed in the Public Domain.


"""clock"""


__author__ = "Bart Thate <programmingobject@gmail.com>"


# IMPORTS


import threading
import time


from opr.objects import Object
from opr.threads import Thread, launch


# INTERFACE


def __dir__():
    return (
            'Repeater',
            'Timer'
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
