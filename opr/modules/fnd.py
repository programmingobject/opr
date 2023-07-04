# This file is placed in the Public Domain.


"find"


import time


from opr.objects import keys, prt
from opr.persist import files, find, fntime
from opr.utility import elapsed


def fnd(event):
    "locate objects"
    if not event.args:
        res = sorted([x.split('.')[-1].lower() for x in files()])
        if res:
            event.reply(",".join(res))
        else:
            event.reply('no types yet.')
        return
    otype = event.args[0]
    nmr = 0
    keyz = None
    if event.gets:
        keyz = ','.join(keys(event.gets))
    if len(event.args) > 1:
        keyz += ',' + ','.join(event.args[1:])
    for obj in find(otype, event.gets):
        if not keyz:
            keyz = ',' + ','.join(keys(obj))
        prnt = prt(obj, keyz)
        lap = elapsed(time.time()-fntime(obj.__oid__))
        event.reply(f'{nmr} {prnt} {lap}')
        nmr += 1
    if not nmr:
        event.reply(f'no result ({event.txt})')
