# This file is placed in the Public Domain.
#
# pylint: disable=C0115,C0116,R0902


"happens"


import threading


from .default import Default


def __dir__():
    return (
            'Event',
           )


__all__ = __dir__()



class Event(Default):

    def __init__(self):
        Default.__init__(self)
        self._ready = threading.Event()
        self._thr = None
        self.result = []

    def ready(self) -> None:
        self._ready.set()

    def reply(self, txt) -> None:
        self.result.append(txt)

    def wait(self) -> []:
        if self._thr:
            self._thr.join()
        self._ready.wait()
        return self.result
