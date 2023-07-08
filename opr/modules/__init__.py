# This file is placed in the Public Domain.


"modules"


from opr.modules import fnd, irc, log, mdl, req, rss, shp, tdo, wsd, wsh


def __dir__():
    return (
            "fnd",
            "irc",
            "log",
            "mdl",
            "req",
            "rss",
            "shp",
            "tdo",
            "wsd",
            "wsh"
           )


__all__ = __dir__()
