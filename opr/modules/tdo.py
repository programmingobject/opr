# This file is placed in the Public Domain.


"todo"


import time


from opr.objects import Object
from opr.persist import find, fntime, write
from opr.utility import elapsed


class Todo(Object):

    "todo object"

    def __init__(self):
        super().__init__()
        self.txt = ''

    def len(self):
        "length"
        return len(self.__dict__)

    def size(self):
        "size"
        return len(self.__dict__)


def dne(event):
    "flag todo as done"
    if not event.args:
        return
    selector = {'txt': event.args[0]}
    for obj in find('todo', selector):
        obj.__deleted__ = True
        write(obj)
        event.reply('ok')
        break


def tdo(event):
    "add a todo"
    if not event.rest:
        nmr = 0
        for obj in find('todo'):
            lap = elapsed(time.time()-fntime(obj.__oid__))
            event.reply(f'{nmr} {obj.txt} {lap}')
            nmr += 1
        if not nmr:
            event.reply("no todo")
        return
    obj = Todo()
    obj.txt = event.rest
    write(obj)
    event.reply('ok')
