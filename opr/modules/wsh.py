# This file is placed in the Public Domain.


"wish lists"


# IMPORTS


import time


from opr.objects import Object, find, fntime, write
from opr.utility import elapsed


# CLASSES


class Wish(Object):

    """wish item"""

    def __init__(self):
        Object.__init__(self)
        self.txt = ''

    def gettxt(self, txt):
        """get text"""
        return self.txt

    def settxt(self, txt):
        """set txt"""
        self.txt = txt


# COMMANDS


def ful(event):
    """full filled a wish"""
    if not event.args:
        return
    selector = {'txt': event.args[0]}
    for obj in find('wish', selector):
        obj.__deleted__ = True
        write(obj)
        event.reply('done')


def wsh(event):
    """add wish"""
    if not event.rest:
        nmr = 0
        for obj in find('wish'):
            lap = elapsed(time.time()-fntime(obj.__oid__))
            event.reply(f'{nmr} {obj.txt} {lap}')
            nmr += 1
        if not nmr:
            event.reply("no wishes")
        return
    obj = Wish()
    obj.txt = event.rest
    write(obj)
    event.reply('ok')
