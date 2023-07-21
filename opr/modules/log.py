# This file is placed in the Public Domain.
#
# pylint: disable=C,I,R


"log text"


import time


from .. import Object
from .. import find, fntime, laps, write


class Log(Object):

    def __init__(self):
        super().__init__()
        self.createtime = time.time()
        self.txt = ''

    def __size__(self):
        return len(self.txt)

    def __since__(self):
        return self.createtime


def log(event):
    if not event.rest:
        nmr = 0
        for obj in find('log'):
            lap = laps(time.time() - fntime(obj.__oid__))
            event.reply(f'{nmr} {obj.txt} {lap}')
            nmr += 1
        if not nmr:
            event.reply('no log')
        return
    obj = Log()
    obj.txt = event.rest
    write(obj)
    event.reply('ok')
