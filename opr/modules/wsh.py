# This file is placed in the Public Domain.
#
# pylint: disable=C,I,R,W0401,W0614


"wish list"


import time


from .. import Object
from .. import find, fntime, laps, write


class Wish(Object):

    def __init__(self):
        Object.__init__(self)
        self.txt = ''

    def gettxt(self):
        return self.txt

    def settxt(self, txt):
        self.txt = txt


def ful(event):
    if not event.args:
        return
    selector = {'txt': event.args[0]}
    for obj in find('wish', selector):
        obj.__deleted__ = True
        write(obj)
        event.reply('done')


def wsh(event):
    if not event.rest:
        nmr = 0
        for obj in find('wish'):
            lap = laps(time.time()-fntime(obj.__oid__))
            event.reply(f'{nmr} {obj.txt} {lap}')
            nmr += 1
        if not nmr:
            event.reply("no wishes")
        return
    obj = Wish()
    obj.txt = event.rest
    write(obj)
    event.reply('ok')
