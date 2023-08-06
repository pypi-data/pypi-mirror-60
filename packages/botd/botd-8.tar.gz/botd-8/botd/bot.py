# BOTD - IRC channel daemon.
#
# virtual bot class.

import queue
import sys

from botd.err import ENOTIMPLEMENTED
from botd.hdl import Handler
from botd.krn import kernels
from botd.obj import Cfg
from botd.thr import launch

def __dir__():
    return ('Bot', 'Cfg')

class Cfg(Cfg):

    def __init__(self, cfg={}):
        super().__init__(cfg)
        self.channel = ""
        self.nick = ""
        self.port = 0
        self.server = ""

class Bot(Handler):

    def __init__(self, cfg={}):
        super().__init__()
        self._outputed = False
        self._outqueue = queue.Queue()
        self.cfg = Cfg(cfg)
        self.channels = []

    def announce(self, txt):
        for channel in self.channels:
            self.say(channel, txt)

    def connect(self):
        raise ENOTIMPLEMENTED

    def input(self):
        while not self._stopped:
            try:
                e = self.poll()
            except EOFError:
                break
            self.put(e)

    def output(self):
        self._outputed = True
        while not self._stopped:
            channel, txt, type = self._outqueue.get()
            if txt:
                self.say(channel, txt, type)

    def poll(self):
        pass

    def raw(self, txt):
        sys.stdout.write(str(txt) + "\n")
        sys.stdout.flush()

    def say(self, channel, txt, mtype="normal"):
        self.raw(txt)

    def start(self, input=False, output=False):
        k = kernels.get_first()
        k.fleet.add(self)
        super().start()
        if output:
            launch(self.output)
        if input:
            launch(self.input)
