import os
import sys

from ccaerrors import errorNotify, errorRaise, errorExit
from dvbctrl.commands import DVBCommand
from dvbctrl.connection import ControlConnection
from dvbctrl.dvbstreamer import DVBStreamer

fnadapters = os.listdir("/dev/dvb/")
adapters = [int(x.replace("adapter", "")) for x in fnadapters]
streamers = [DVBStreamer(x) for x in adapters]


def startAll():
    try:
        for streamer in streamers:
            if not streamer.isRunning():
                streamer.start()
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


def stopAll():
    try:
        for streamer in streamers:
            streamer.stop()
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


def findFreeAdapter(mux):
    try:
        pass
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


def muxForChannel(channel):
    # any adapter will do
    try:
        dvbc = DVBCommand()
        dvbc.open()
        errmsg, lines = dvbc.doCommand("serviceinfo '{channel}'")
        dvbc.close()
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)
