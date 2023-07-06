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
            if "mod" not in obj:
                obj["mod"] = ""
            for val in spl(value):
                if val not in obj["mod"]:
                    obj["mod"] += f",{val}"
            return True
        if "sets" not in  obj:
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


def parse(obj, txt):
    "parse text for commands and arguments/options"
    obj["cmd"] = ""
    obj["otxt"] = txt
    splitted = txt.split()
    args = []
    _nr = -1
    for word in splitted:
        if parseoption(obj, word):
            continue
        if parsequal(obj, word):
            continue
        if parseassign(obj, word):
            continue
        _nr += 1
        if _nr == 0:
            obj["cmd"] = word
            continue
        args.append(word)
    if args:
        obj["args"] = args
        obj["rest"] = ' '.join(args)
        obj["txt"] = obj["cmd"] + ' ' + obj["rest"]
    else:
        obj["txt"] = obj["cmd"]
    return obj


def spl(txt2) -> []:
    "split comma seperated string" 
    try:
        res = txt2.split(',')
    except (TypeError, ValueError):
        res = txt2
    return [x for x in res if x]
