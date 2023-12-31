# This file is placed in the Public Domain.
#
# pylint: disable=C0115,C0116,R0903,W0105


"todo list"


import time


from ..persist import Persist
from ..storage import find, write
from ..utility import fntime, laps


"classes"


class Todo(Persist):

    def __init__(self):
        Persist.__init__(self)
        self.txt = ''


"commands"


def dne(event):
    if not event.args:
        event.reply("dne <txt>")
        return
    selector = {'txt': event.args[0]}
    nmr = 0
    for obj in find('todo', selector):
        nmr += 1
        obj.__deleted__ = True
        write(obj)
        event.reply('ok')
        break
    if not nmr:
        event.reply("nothing todo")


def tdo(event):
    if not event.rest:
        nmr = 0
        for obj in find('todo'):
            lap = laps(time.time()-fntime(obj.__oid__))
            event.reply(f'{nmr} {obj.txt} {lap}')
            nmr += 1
        if not nmr:
            event.reply("no todo")
        return
    obj = Todo()
    obj.txt = event.rest
    write(obj)
    event.reply('ok')
