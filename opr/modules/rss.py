# This file is placed in the Public Domain.


"rich site syndicate"


import html.parser
import re
import threading
import time
import urllib
import _thread


from urllib.error import HTTPError, URLError
from urllib.parse import quote_plus, urlencode
from urllib.request import Request, urlopen


from opr.handler import Bus, Cfg
from opr.objects import Default, Object, prt, update
from opr.persist import find, fntime, last, write
from opr.repeats import Repeater
from opr.threads import launch, threaded
from opr.utility import elapsed, spl


def start():
    "start a fetcher"
    fetcher = Fetcher()
    fetcher.start()
    return fetcher


fetchlock = _thread.allocate_lock()


class Feed(Default):

    "represent a rss feed"

    def len(self):
        "length"
        return len(self.__dict__)

    def size(self):
        "size"
        return len(self.__dict__)


class Rss(Object):

    "save rss item"

    def __init__(self):
        super().__init__()
        self.display_list = 'title,link,author'
        self.name = ''
        self.rss = ''

    def len(self):
        "length"
        return len(self.__dict__)

    def size(self):
        "size"
        return len(self.__dict__)


class Seen(Object):

    "list of seen urls"

    def __init__(self):
        super().__init__()
        self.urls = []

    def len(self):
        "length" 
        return len(self.__dict__)

    def size(self):
        "size"
        return len(self.__dict__)


class Fetcher(Object):

    "rss feed fetcher"

    dosave = False
    seen = Seen()

    def __init__(self):
        super().__init__()
        self.connected = threading.Event()

    @staticmethod
    def display(obj):
        "display rss item"
        result = ''
        displaylist = []
        try:
            displaylist = obj.display_list or 'title,link'
        except AttributeError:
            displaylist = 'title,link,author'
        for key in spl(displaylist):
            if not key:
                continue
            data = getattr(obj, key, None)
            if not data:
                continue
            data = data.replace('\n', ' ')
            data = striphtml(data.rstrip())
            data = unescape(data)
            result += data.rstrip()
            result += ' - '
        return result[:-2].rstrip()

    def fetch(self, feed):
        "fetch updates"
        with fetchlock:
            counter = 0
            objs = []
            for obj in reversed(list(getfeed(feed.rss, feed.display_list))):
                fed = Feed()
                update(fed, obj)
                update(fed, feed)
                if 'link' in fed:
                    url = urllib.parse.urlparse(fed.link)
                    if url.path and not url.path == '/':
                        uurl = f'{url.scheme}://{url.netloc}/{url.path}'
                    else:
                        uurl = fed.link
                    if uurl in Fetcher.seen.urls:
                        continue
                    Fetcher.seen.urls.append(uurl)
                counter += 1
                if self.dosave:
                    write(fed)
                objs.append(fed)
        if objs:
            write(Fetcher.seen)
        txt = ''
        feedname = getattr(feed, 'name')
        if feedname:
            txt = f'[{feedname}] '
        for obj in objs:
            txt2 = txt + self.display(obj)
            Bus.announce(txt2.rstrip())
        return counter

    def run(self):
        "run fetching updates of all feeds"
        thrs = []
        for feed in find('rss'):
            thrs.append(launch(self.fetch, feed))
        return thrs

    def start(self, repeat=True):
        "start fetcher"
        last(Fetcher.seen)
        if repeat:
            repeater = Repeater(300.0, self.run)
            repeater.start()


class Parser(Object):

    "parse rss feed"

    @staticmethod
    def getitem(line, item):
        "return xml items in rss feed"
        lne = ''
        try:
            index1 = line.index(f'<{item}>') + len(item) + 2
            index2 = line.index(f'</{item}>')
            lne = line[index1:index2]
            if 'CDATA' in lne:
                lne = lne.replace('![CDATA[', '')
                lne = lne.replace(']]', '')
                lne = lne[1:-1]
        except ValueError:
            lne = None
        return lne

    @staticmethod
    def parse(txt, item='title,link'):
        "parse text for xml items"
        res = []
        for line in txt.split('<item>'):
            line = line.strip()
            obj = Object()
            for itm in spl(item):
                setattr(obj, itm, Parser.getitem(line, itm))
            res.append(obj)
        return res


def getfeed(url, item):
    "fetch feed"
    if Cfg.debug:
        return [Object(), Object()]
    try:
        result = geturl(url)
    except (ValueError, HTTPError, URLError):
        return [Object(), Object()]
    if not result:
        return [Object(), Object()]
    return Parser.parse(str(result.data, 'utf-8'), item)


def gettinyurl(url):
    "fetch feed using tinyurl"
    postarray = [
        ('submit', 'submit'),
        ('url', url),
    ]
    postdata = urlencode(postarray, quote_via=quote_plus)
    req = Request('http://tinyurl.com/create.php',
                  data=bytes(postdata, 'UTF-8'))
    req.add_header('User-agent', useragent(url))
    with urlopen(req) as htm:
        for txt in htm.readlines():
            line = txt.decode('UTF-8').strip()
            i = re.search('data-clipboard-text="(.*?)"', line, re.M)
            if i:
                return i.groups()
    return []


def geturl(url):
    "fetch url"
    url = urllib.parse.urlunparse(urllib.parse.urlparse(url))
    req = urllib.request.Request(url)
    req.add_header('User-agent', useragent("rss fetcher"))
    with urllib.request.urlopen(req) as response:
        response.data = response.read()
        return response


def striphtml(text):
    "strip html"
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)


def unescape(text):
    "unescape html"
    txt = re.sub(r'\s+', ' ', text)
    return html.unescape(txt)


def useragent(txt):
    "return useragent string"
    return 'Mozilla/5.0 (X11; Linux x86_64) ' + txt


def dpl(event):
    "set items to display"
    if len(event.args) < 2:
        event.reply('dpl <stringinurl> <item1,item2>')
        return
    setter = {'display_list': event.args[1]}
    for feed in find('rss', {'rss': event.args[0]}):
        if feed:
            update(feed, setter)
            write(feed)
    event.reply('ok')


@threaded
def ftc(event):
    "fetch feeds"
    res = []
    thrs = []
    fetcher = Fetcher()
    fetcher.start(False)
    thrs = fetcher.run()
    for thr in thrs:
        res.append(thr.join())
    if res:
        event.reply(','.join([str(x) for x in res if x]))
        return


def nme(event):
    "give feed an display name"
    if len(event.args) != 2:
        event.reply('name <stringinurl> <name>')
        return
    selector = {'rss': event.args[0]}
    for feed in find('rss', selector):
        if feed:
            feed.name = event.args[1]
            write(feed)
    event.reply('ok')


def rem(event):
    "remove feed"
    if len(event.args) != 1:
        event.reply('rem <stringinurl>')
        return
    selector = {'rss': event.args[0]}
    for feed in find('rss', selector):
        if feed:
            feed.__deleted__ = True
            write(feed)
    event.reply('ok')


def rss(event):
    "add feed"
    if not event.rest:
        nrs = 0
        for feed in find('rss'):
            elp = elapsed(time.time()-fntime(feed.__oid__))
            txt = prt(feed)
            event.reply(f'{nrs} {txt} {elp}')
            nrs += 1
        if not nrs:
            event.reply('no rss feed found.')
        return
    url = event.args[0]
    if 'http' not in url:
        event.reply('i need an url')
        return
    for res in find('rss', {'rss': url}):
        if res:
            event.reply(f'already got {url}')
            return
    feed = Rss()
    feed.rss = event.args[0]
    write(feed)
    event.reply('ok')
