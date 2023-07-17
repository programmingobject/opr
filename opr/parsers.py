# This file is placed in the Public Domain.
#
# pylint: disable=C,I,R


"parse events"


__author__ = "Bart Thate <programmingobject@gmail.com>"


def __dir__():
    return (
            "parse",
           )


__all__ = __dir__()


def parse(obj, txt):
    obj.cmd = obj.cmd or ""
    obj.args = obj.args or []
    obj.gets = obj.gets or {}
    obj.mod = obj.mod or ""
    obj.opts = obj.opts or ""
    obj.otxt = txt or ""
    obj.rest = obj.rest or ""
    obj.sets = obj.sets or {}
    for spli in txt.split():
        if spli.startswith("-"):
            try:
                obj.index = int(spli[1:])
            except ValueError:
                obj.opts += spli[1:]
            continue
        if "=" in spli:
            key, value = spli.split("=", maxsplit=1)
            if key == "mod":
                obj.mod += "," + value
                continue
            obj.sets[key] = value
            continue
        if "==" in spli:
            key, value = spli.split("==", maxsplit=1)
            obj.gets[key] = value
            continue
        if not obj.cmd:
            obj.cmd = spli
            continue
        obj.args.append(spli)
    obj.txt = obj.cmd
    if obj.args:
        obj.rest = str(" ".join(obj.args))
        if obj.rest:
            obj.txt += " " + obj.rest
