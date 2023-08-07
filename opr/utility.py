# This file is placed in the Public Domain.
#
# pylint: disable=C0116,W0212


"utilities"


import os
import time


def __dir__():
    return (
            'banner',
            'listmods',
            'parse',
            'tme',
            'wait'
           )


__all__ = __dir__()


def banner(cfg):
    if cfg.mod:
        mods = cfg.mod.upper()
    else:
        mods = "CONSOLE"
    return f"{cfg.name.upper()} started {tme()} {mods} {cfg.opts.upper()}"


def listmods(path):
    return [
            x[:-3].strip() for x in os.listdir(path)
            if x.endswith(".py")
            and x not in ["__init__.py", "__main__.py"]
           ]


def parse(self, txt=None) -> None:
    args = []
    self.args = []
    self.cmd = self.cmd or ""
    self.gets = self.gets or {}
    self.mod = self.mod or ""
    self.opts = self.opts or ""
    self.sets = self.sets or {}
    self.otxt = txt or ""
    _nr = -1
    for spli in self.otxt.split():
        if spli.startswith("-"):
            try:
                self.index = int(spli[1:])
            except ValueError:
                self.opts += spli[1:]
            continue
        if "=" in spli:
            key, value = spli.split("=", maxsplit=1)
            if key == "mod":
                if self.mod:
                    self.mod += f",{value}"
                else:
                    self.mod = value
                continue
            self.sets[key] = value
            continue
        if "==" in spli:
            key, value = spli.split("==", maxsplit=1)
            self.gets[key] = value
            continue
        _nr += 1
        if _nr == 0:
            self.cmd = spli
            continue
        args.append(spli)
    if args:
        self.args = args
        self.txt = self.cmd or ""
        self.rest = " ".join(self.args)
        self.txt = self.cmd + " " + self.rest
    else:
        self.txt = self.cmd


def tme():
    return " ".join(time.ctime(time.time()).split()[1:])


def wait(func=None):
    while 1:
        time.sleep(1.0)
        if func:
            func()
