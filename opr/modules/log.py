# This file is placed in the Public Domain.
#
# pylint: disable=C0115,C0116


"log text"


import time


from ..persist import find, write
from ..storage import Data
from ..utility import fntime, laps


class Log(Data):

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
