# This file is placed in the Public Domain.


"modules"


from opr.modules import fnd, irc, log, mdl, req, rss, shp, tdo, wsd


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
            "wsd"
           )


__all__ = __dir__()
