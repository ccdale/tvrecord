from signal import signal, SIGINT, SIGTERM, SIGHUP
import sys
from threading import Event

from ccaerrors import errorNotify, errorRaise, errorExit
from dvbctrl.commands import DVBCommand
from dvbctrl.dvbstreamer import DVBStreamer

import tvrecord
import tvrecord.tvrecorder as recorder

log = recorder.log
doexit = Event()


def interruptMonitor(signrcvd, frame):
    try:
        log.info(f"{signrcvd=} Interrupt received in monitor module - stopping.")
        doexit.set()
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


# if we get a `ctrl-c` from the keyboard, kill -15, or kill -1 stop immediately
# by going to the interruptMonitor above
signal(SIGINT, interruptMonitor)
signal(SIGTERM, interruptMonitor)
signal(SIGHUP, interruptMonitor)


def doTasks(cf, eng):
    """iterate through the tasks"""
    try:
        pass
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


def shutDown():
    try:
        cf.writeConfig()
        recorder.stopAll()
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


def monitor(debug=False):
    """wake up, kick off any task, sleep, repeat"""
    try:
        log.info(f"DVB Monitor version {tvrecord.__version__} starting")
        if len(recorder.streamers) == 0:
            raise Exception("No DVBStreamers found")
        recorder.startAll()
        cf, eng = tvrecord.begin(debug=debug)
        sleeptime = int(cf.get("sleeptime", "60"))
        log.debug("while loop starting, hello.")
        while not doexit.is_set():
            doTasks(cf, eng)
            log.debug(f"Waiting for {sleeptime} seconds")
            doexit.wait(sleeptime)
        log.debug("while loop exiting, bye")
        log.info("Shutting down DVB Monitor")
        shutDown(cf)
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


if __name__ == "__main__":
    monitor(debug=True)
