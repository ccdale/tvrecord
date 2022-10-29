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
sleeptime = 60


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


def doTasks():
    """iterate through the tasks"""
    try:
        pass
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


def shutDown():
    try:
        pass
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


def startUp():
    try:
        pass
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


def monitor():
    """wake up, kick off any task, sleep, repeat"""
    try:
        log.info(f"DVB Monitor version {tvrecord.__version__} starting")
        startUp()
        log.debug("while loop starting, hello.")
        while not doexit.is_set():
            doTasks()
            log.debug(f"Waiting for {sleeptime} seconds")
            doexit.wait(sleeptime)
        log.debug("while loop exiting, bye")
        log.info("Shutting down DVB Monitor")
        shutDown()
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


if __name__ == "__main__":
    monitor()
