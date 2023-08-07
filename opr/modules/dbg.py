# This file is placed in the Public Domain.
#
# pylint: disable=C0116,W0719


"debug"


from ..runtime import Cfg


def dbg(event):
    if Cfg.error:
        event.reply("raising")
        raise Exception("debug")
    event.reply("error is not enabled")
