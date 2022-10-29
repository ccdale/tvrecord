import os
import sys

from ccaerrors import errorNotify, errorRaise, errorExit
import ccalogging

from dvbctrl.commands import DVBCommand
from dvbctrl.connection import ControlConnection
from dvbctrl.dvbstreamer import DVBStreamer

__appname__ = "tvrecorder"
home = os.path.expanduser("~/")
logd = os.path.join(home, "log")
res = os.makedirs(logd, exist_ok=True)
logfn = os.path.join(logd, f"{__appname__}.log")
ccalogging.setLogFile(logfn, rotation=30)
# ccalogging.setInfo()
ccalogging.setDebug()
log = ccalogging.log

fnadapters = os.listdir("/dev/dvb/")
adapters = [int(x.replace("adapter", "")) for x in fnadapters]
streamers = [DVBStreamer(x) for x in adapters]


def startAll():
    try:
        for streamer in streamers:
            if not streamer.isRunning():
                log.debug(f"starting dvbstreamer on adapter {streamer.adapter}")
                streamer.start()
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


def stopAll():
    try:
        for streamer in streamers:
            log.debug(f"stopping dvbstreamer on adapter {streamer.adapter}")
            streamer.stop()
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


def findFreeAdapter(mux, channel):
    try:
        pass
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


def muxForChannel(channel):
    # any adapter will do
    try:
        dvbc = DVBCommand()
        dvbc.open()
        lines = dvbc.serviceinfo(channel)
        dvbc.close()
        return lines[0]
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)
