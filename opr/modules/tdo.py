# This file is placed in the Public Domain.
#
# pylint: disable=C,I,R


"todo list"


import time


from .. import Object
from .. import laps, find, fntime, write


class Todo(Object):

    def __init__(self):
        super().__init__()
        self.txt = ''

    def len(self):
        return 0

    def size(self):
        return len(self.__dict__)


def dne(event):
    if not event.args:
        return
    selector = {'txt': event.args[0]}
    for obj in find('todo', selector):
        obj.__deleted__ = True
        write(obj)
        event.reply('ok')
        break


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
