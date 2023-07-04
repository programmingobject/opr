# This file is placed in the Public Domain.


"udp to irc relay"


import select
import socket
import sys
import time


from opr.handler import Bus
from opr.objects import Default, Object
from opr.persist import last
from opr.threads import launch


def start():
    "start udp server"
    udpd = UDP()
    udpd.start()
    return udpd


class Cfg(Default):

    "udp configuration"

    def __init__(self):
        super().__init__()
        self.host = "localhost"
        self.port = 5500

    def len(self):
        "length"
        return self.server

    def size(self):
        "size"
        return self.port

class UDP(Object):

    "udp to irc relay"

    def __init__(self):
        super().__init__()
        self.stopped = False
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self._sock.setblocking(1)
        self._starttime = time.time()
        self.cfg = Cfg()
        self.cfg.addr = ""

    def output(self, txt, addr=None):
        "output text on listeners bus"
        if addr:
            self.cfg.addr = addr
        Bus.announce(txt.replace("\00", ""))

    def server(self):
        "listen on udp socket"
        try:
            self._sock.bind((self.cfg.host, self.cfg.port))
        except socket.gaierror:
            return
        while not self.stopped:
            (txt, addr) = self._sock.recvfrom(64000)
            if self.stopped:
                break
            data = str(txt.rstrip(), "utf-8")
            if not data:
                break
            self.output(data, addr)

    def exit(self):
        "exit loop"
        self.stopped = True
        self._sock.settimeout(0.01)
        self._sock.sendto(bytes("exit", "utf-8"), (self.cfg.host, self.cfg.port))

    def start(self):
        "start udp listening loop"
        last(self.cfg)
        launch(self.server)


def toudp(host, port, txt):
    "function to send udp text"
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(bytes(txt.strip(), "utf-8"), (host, port))


def udp(event):
    "command to send udp"
    cfg = Cfg()
    last(cfg)
    if len(sys.argv) > 2:
        txt = " ".join(sys.argv[2:])
        toudp(cfg.host, cfg.port, txt)
        return
    if not select.select([sys.stdin, ], [], [], 0.0)[0]:
        return
    size = 0
    while 1:
        try:
            (inp, _out, err) = select.select([sys.stdin,], [], [sys.stderr,])
        except KeyboardInterrupt:
            return
        if err:
            break
        stop = False
        for sock in inp:
            txt = sock.readline()
            if not txt:
                stop = True
                break
            size += len(txt)
            toudp(cfg.host, cfg.port, txt)
        if stop:
            break
    event.reply(f"send {size}")
