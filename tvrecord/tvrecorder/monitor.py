import datetime
import os
from signal import signal, SIGINT, SIGTERM, SIGHUP
import sys
from threading import Event
import time

from ccaerrors import errorNotify, errorRaise, errorExit
import ccalogging
from ccautils.fileutils import sizeof_fmt
from dvbctrl.commands import DVBCommand
from dvbctrl.dvbstreamer import DVBStreamer
from dvbctrl.recorder import Recorder
from slugify import slugify

import tvrecord
from tvrecord.tvrecorddb.wrangler import (
    addRecording,
    getLastSize,
    getScheduleRecord,
    unsetScheduleRecord,
    updateSize,
)
from tvrecord.tvrecorder.monitorrecorder import MonitorRecorder

__appname__ = "tvrecord"
home = os.path.expanduser("~/")
logd = os.path.join(home, "log")
res = os.makedirs(logd, exist_ok=True)
logfn = os.path.join(logd, f"{__appname__}.log")
ccalogging.setLogFile(logfn, rotation=30)
ccalogging.setInfo()
log = ccalogging.log

fnadapters = os.listdir("/dev/dvb/")
adapters = [int(x.replace("adapter", "")) for x in fnadapters]
streamers = [DVBStreamer(x) for x in adapters]

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


def startUp():
    """Start each streamer

    tune each adapter to a different mux
    """
    try:
        log.debug(f"starting {len(adapters)} streamers")
        [s.start() for s in streamers if not s.isRunning()]
        dvbc = DVBCommand(adapters[0])
        muxes = dvbc.lsmuxes()
        log.debug(f"mux list: {muxes}")
        for cn, a in enumerate(adapters):
            dvbc = DVBCommand(a)
            chans = dvbc.lsservices(muxes[cn])
            log.debug(f"chan list for mux {muxes[cn]}: {chans}")
            if len(chans):
                log.info(f"Tuning adapter {a} to mux {muxes[cn]} (channel {chans[0]})")
                if not dvbc.tuneToChannel(chans[0]):
                    log.error(
                        f"Failed to tune to channel {chans[0]} on mux {muxes[cn]}"
                    )
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


def shutDown(cf):
    try:
        log.debug("writing config")
        cf.writeConfig()
        log.info("stopping dvbstreamers")
        [s.stop() for s in streamers if s.isRunning()]
        for s in streamers:
            if s.isRunning():
                log.error(f"Failed to stop streamer on adapter {s.adapter}")
            else:
                log.debug(f"Stopped streamer on adapter {s.adapter}")
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


def findFreeAdapter():
    try:
        free = None
        for s in streamers:
            dvbc = DVBCommand(s.adapter)
            output = dvbc.getmrl()
            if output[0].startswith("null"):
                return s.adapter
        return None
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


def muxForChannel(channel):
    # any adapter will do, pick the first off of the list
    try:
        dvbc = DVBCommand(str(adapters[0]))
        dvbc.open()
        lines = dvbc.serviceinfo(channel)
        dvbc.close()
        return lines[0]
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


def nextStart(upcoming, startpad, endpad):
    try:
        now = time.time()
        nextstart = upcoming[0]["schedule"]["airdate"] - startpad
        if nextstart <= now:
            return upcoming[0]
        else:
            return None
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


def startRecording(cf, eng, nextrecording):
    try:
        fnstub = makeFileNameStub(nextrecording)
        if not unsetScheduleRecord(eng, nextrecording["schedule"]):
            raise Exception(
                f"Failed to unset record flag in schedule: {nextrecording=}"
            )
        adapter = findFreeAdapter()
        if adapter is None:
            raise Exception(
                f"failed to find a free adapter for recording: {nextrecording=}"
            )
        fqfn = os.path.join(cf.get("recordingsdir"), f"{fnstub}.ts")
        nfofn = os.path.join(cf.get("recordingsdir"), f"{fnstub}.nfo")
        rid = addRecording(cf, eng, nextrecording, fqfn, adapter)
        starttime = nextrecording["schedule"]["airdate"] - cf.get("startpad")
        endtime = (
            nextrecording["schedule"]["airdate"]
            + nextrecording["schedule"]["duration"]
            + int(cf.get("endpad"))
        )
        kwargs = {
            "adapter": adapter,
            "starttime": starttime,
            "endtime": endtime,
        }
        title = nextrecording["program"]["title"]
        channel = nextrecording["channel"]["dvbname"]
        args = [nextrecording["channel"]["dvbname"], fqfn]
        m = MonitorRecorder(*args, **kwargs)
        log.info(f"starting to record {title} on {channel}")
        log.info(f"{m}")
        m.start()
        # Ochan = nextrecording["channel"]["dvbname"]
        # r = Recorder(chan, fqfn, adapter=adapter)
        # r.start()
        # m = MonitorRecorder(chan, fqfn, adapter=adapter

        # TODO make nfo file
        return (m, rid)
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


def makeFileNameStub(nextrecording):
    try:
        program = nextrecording["program"]
        txt = program["title"]
        if "episodetitle" in program and len(program["episodetitle"]):
            txt = f"{txt}-{program['episodetitle']}"
        if "series" in program and program["series"] is not None:
            sp = program["series"]
            s = f"S0{sp}" if sp < 10 else f"S{sp}"
            if "episode" in program and program["episode"] is not None:
                ep = program["episode"]
                e = f"E0{ep}" if ep < 10 else f"E{ep}"
            else:
                e = ""
            txt = f"{txt}-{s}{e}"
        title = slugify(txt)
        ts = makeTs()
        return f"{ts}-{title}"
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


def makeTs(dt=None):
    try:
        if dt is None:
            dt = datetime.datetime.today()
        ts = f"{dt:%Y%m%d%H%M%S}"
        return ts
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


def doTasks(cf, eng, recs):
    """iterate through the tasks"""
    try:
        now = time.time()
        for r, rid in recs:
            growing, size = r.check(r.lastsize)
            if not growing:
                log.warning(f"recording has stopped growing: {r}")
            else:
                r.lastsize = size
            if r.endtime < now:
                log.info(
                    f"stopping recording of file {r.fqfn}, size: {sizeof_fmt(size)}"
                )
                r.stop()
                r.completed = True
                growing, size = r.check(0)
                updateSize(eng, rid, size)
        m = None
        rid = None
        rdir = cf.get("recordingsdir")
        upcoming = getScheduleRecord(eng)
        if len(upcoming):
            ns = nextStart(upcoming, cf.get("startpad"), cf.get("endpad"))
            if ns is not None:
                m, rid = startRecording(cf, eng, ns)
        return (m, rid)
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


def monitor(debug=False):
    """wake up, kick off any task, sleep, repeat"""
    try:
        log.info(f"DVB Monitor version {tvrecord.__version__} starting")
        if len(streamers) == 0:
            raise Exception("No DVBStreamers found")
        startUp()
        log.info(f"found, started and tuned {len(streamers)} DVBStreamers")
        mfc = muxForChannel("Sky News")
        log.debug(f"{mfc=}")
        cf, eng = tvrecord.begin(debug=debug)
        sleeptime = int(cf.get("sleeptime", "60"))
        recs = []
        log.debug("while loop starting, hello.")
        while not doexit.is_set():
            m, rid = doTasks(cf, eng, recs)
            if m is not None:
                recs.append((m, rid))
            remove = []
            for m, rid in recs:
                if m.completed:
                    remove.append((m, rid))
            for m, rid in remove:
                log.debug(f"{m} has completed. removing")
                recs.remove((m, rid))
            doexit.wait(sleeptime)
        log.debug("while loop exiting, bye")
        log.info("Shutting down DVB Monitor")
        shutDown(cf)
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


if __name__ == "__main__":
    ccalogging.setDebug()
    # monitor()
    monitor(debug=True)
