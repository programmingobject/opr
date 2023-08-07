# This file is placed in the Public Domain.
#
# pylint: disable=C0116


"errors"


import io
import traceback


from ..errored import Errors


def err(event):
    if not Errors.errors:
        event.reply("no errors")
        return
    for exc in Errors.errors:
        stream = io.StringIO(
                             traceback.print_exception(
                                                       type(exc),
                                                       exc,
                                                       exc.__traceback__
                                                      )
                            )
        for line in stream.readlines():
            event.reply(line)
