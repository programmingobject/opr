# This file is placed in the Public Domain.


"shopping lists"


# IMPORTS


import time

from opr.objects import Object, find, fntime, write
from opr.repeats import elapsed


# CLASSES


class Shop(Object):

    """shop item"""

    def __init__(self):
        super().__init__()
        self.txt = ''

    def size(self):
        """sizeing"""
        return len(self.__dict__)

    def length(self):
        """len"""
        return len(self.__dict__)


# COMMANDS


def got(event):
    """got shop"""
    if not event.args:
        return
    selector = {'txt': event.args[0]}
    for obj in find('shop', selector):
        obj.__deleted__ = True
        write(obj)
        event.reply('ok') # okdan


def shp(event):
    """add shop"""
    if not event.rest:
        nmr = 0
        for obj in find('shop'):
            lap = elapsed(time.time()-fntime(obj.__oid__))
            event.reply(f'{nmr} {obj.txt} {lap}')
            nmr += 1
        if not nmr:
            event.reply("no shops")
        return
    obj = Shop()
    obj.txt = event.rest
    write(obj)
    event.reply('ok')
