# This file is placed in the Public Domain.


"parsing"


# DEFINES


def __dir__():
    return (
            "parse",
            "parse_cli"
           ) 


__all__ = __dir__()


def parsequal(obj, word):
    "check for qualness"
    try:
        key, value = word.split('==')
        if not obj["skip"]:
            obj["skip"] = {}
        if value.endswith('-'):
            value = value[:-1]
            obj["skip"][key] = value
        if not obj["gets"]:
            obj["gets"] = Default()
        obj[key] = value
        return True
    except ValueError:
        return False


def parseassign(obj, word):
    "check for assign"
    try:
        key, value = word.split('=', maxsplit=1)
        if key == "mod":
            if not obj["mod"]:
                obj["mod"] = ""
            for val in spl(value):
                if val not in obj["mod"]:
                    obj["mod"] += f",{val}"
            return True
        if not obj["sets"]:
            obj["sets"] = {}
        obj["sets"][key] = value
        return True
    except ValueError:
        return False


def parseoption(obj, word):
    "check for options"
    if word.startswith('-'):
        if "index" not in obj:
            obj["index"] = 0
        try:
            obj["index"] = int(word[1:])
        except ValueError:
            if "opts" not in obj:
                obj["opts"] = ""
            obj["opts"] = obj["opts"] + word[1:]
        return True
    return False


def parse(txt):
    "parse text for commands and arguments/options"
    res = {}
    res["cmd"] = ""
    res["otxt"] = txt
    splitted = txt.split()
    args = []
    _nr = -1
    for word in splitted:
        if parseoption(res, word):
            continue
        if parsequal(res, word):
            continue
        if parseassign(res, word):
            continue
        _nr += 1
        if _nr == 0:
            res["cmd"] = word
            continue
        args.append(word)
    if args:
        res["args"] = args
        res["rest"] = ' '.join(args)
        res["txt"] = res["cmd"] + ' ' + res["rest"]
    else:
        res["txt"] = res["cmd"]
    return res
