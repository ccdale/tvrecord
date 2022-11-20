#
# Copyright (c) 2022, Chris Allison
#
#     This file is part of tvrecord.
#
#     tvrecord is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     tvrecord is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with tvrecord.  If not, see <http://www.gnu.org/licenses/>.
#
"""Data wrangler module for tvrecorddb."""
import sys
import time

from ccaerrors import errorNotify, errorExit
import ccalogging
from sqlalchemy.orm import Session

from tvrecord.strings import dateTimeString
from tvrecord.tvrecorddb import searchZap, chooseName, chooseGetData
from tvrecord.tvrecorddb.models import (
    Channel,
    Schedulemd5,
    Schedule,
    Person,
    Personmap,
    Program,
    Recording,
)

log = ccalogging.log


def addUpdateSMD5(sd, smd5, chanid, xdate, session):
    try:
        md5 = session.query(Schedulemd5).filter_by(md5=smd5["md5"]).first()
        if md5:
            return False
        sdate = f"{xdate}T00:00:00Z"
        datets = sd.getTimeStamp(sdate)
        kwargs = {
            "md5": smd5["md5"],
            "stationid": chanid,
            "datestr": sdate,
            "datets": datets,
            "modified": sd.getTimeStamp(smd5["lastModified"]),
        }
        md5 = Schedulemd5(**kwargs)
        session.add(md5)
        return True
    except Exception as e:
        # msg = f"{e}\n{smd5=}, {chanid=}, {xdate=}\n"
        # msg += f"{kwargs=}"
        errorExit(sys.exc_info()[2], e)


def schedulesMd5(sd, eng):
    try:
        retrieve = {}
        with Session(eng) as session, session.begin():
            #
            # xall = session.query(Channel).all()
            #
            xsome = session.query(Channel).filter(Channel.getdata > 0).all()
            # clist = Station.query.filter_by(getdata=1).all()
            # log.info(f"retrieving MD5 hashes for {len(clist)} / {len(xall)} channels")
            #
            # slist = [x.stationid for x in xall]
            #
            # print([x.name for x in xsome])
            slist = [x.stationid for x in xsome]
            smd5 = sd.getScheduleMd5(slist)
            for chan in smd5:
                log.debug(f"scheduleMd5: {chan=}")
                for xdate in smd5[chan]:
                    log.debug(f"scheduleMd5: {xdate=}")
                    if addUpdateSMD5(sd, smd5[chan][xdate], chan, xdate, session):
                        if chan not in retrieve:
                            retrieve[chan] = []
                        retrieve[chan].append(xdate)
        log.debug(f"sheduleMd5 returns: {retrieve=}")
        return retrieve
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


def favourites(eng, favs=True):
    try:
        gd = 1 if favs else 0
        with Session(eng) as session, session.begin():
            xfavs = (
                session.query(Channel)
                .filter(Channel.getdata > gd)
                .order_by(Channel.channelnumber)
                .all()
            )
            xfavs = [x._todict_() for x in xfavs]
        return xfavs
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


def schedules(sd, eng):
    try:
        cleanSchedule(eng)
        log.info("Retrieving schedule hashes")
        xdat = schedulesMd5(sd, eng)
        log.info(f"require schedules for {len(xdat)} channels")
        if len(xdat) > 0:
            chans = [
                {"stationID": str(chanid), "date": xdat[chanid]} for chanid in xdat
            ]
            scheds = sd.getSchedules(chans)
            log.info("Updating new schedules")
            for sched in scheds:
                addSchedule(sd, sched, eng)
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


def removeOverlaps(chanid, start, duration, session):
    try:
        removed = False
        end = start + duration
        xs = (
            session.query(Schedule)
            .filter(
                Schedule.stationid == chanid,
                (Schedule.airdate + Schedule.duration) > start,
                Schedule.airdate < end,
            )
            .all()
        )
        if len(xs) > 0:
            removed = True
            [session.delete(x) for x in xs]
            # db.session.commit()
        return removed
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


def cleanSchedule(eng):
    try:
        # 7 days old schedules now, to facilitate catch up
        yesterday = int(time.time()) - (86400 * 7)
        with Session(eng) as session, session.begin():
            n = session.query(Schedule).count()
            old = session.query(Schedule).filter(Schedule.airdate < yesterday).all()
            dn = len(old)
            [session.delete(x) for x in old]
        log.info(f"Cleaned {dn} rows from {n} Schedules.")
    except Exception as e:
        errorExit(sys.exc_info()[2], e)


def addSchedule(sd, sched, eng):
    try:
        plist = []
        chanid = sched["stationID"]
        startdate = "unknown date"
        if "metadata" in sched and "startDate" in sched["metadata"]:
            startdate = sched["metadata"]["startDate"]
        with Session(eng) as session, session.begin():
            c = session.query(Channel).filter_by(stationid=chanid).first()
            log.info(
                f"Updating schedule for channel {c.name} with {len(sched['programs'])} programs on {startdate}"
            )
            for prog in sched["programs"]:
                kwargs = {
                    "programid": prog["programID"],
                    "stationid": chanid,
                    "airdate": sd.getTimeStamp(prog["airDateTime"]),
                }

                duration = int(prog["duration"])
                removed = removeOverlaps(chanid, kwargs["airdate"], duration, session)
                s = session.query(Schedule).filter_by(**kwargs).first()
                if s and not removed:
                    s.md5 = prog["md5"]
                    s.duration = duration
                    log.debug(f"update schedule: {kwargs=}")
                else:
                    kwargs["md5"] = prog["md5"]
                    kwargs["duration"] = duration
                    log.debug(f"addSchedule: {kwargs=}")
                    s = Schedule(**kwargs)
                    session.add(s)
            # db.session.commit()
            for prog in sched["programs"]:
                p = (
                    session.query(Program)
                    .filter_by(programid=prog["programID"], md5=prog["md5"])
                    .first()
                )
                if not p:
                    plist.append(prog["programID"])
            cn = len(plist)
            if cn > 0:
                log.info(
                    f"require downloading of {cn} programs for {c.name} on {startdate}"
                )
                updatePrograms(sd, plist, session)
    except Exception as e:
        errorExit(sys.exc_info()[2], e)


def updatePrograms(sd, plist, session):
    """Retrieves information for each program in the list"""
    try:
        if len(plist) == 0:
            raise Exception("updatePrograms: received empty list")
        progs = sd.getPrograms(plist)
        [addUpdateProgram(prog, session) for prog in progs]
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


def addUpdateProgram(prog, session):
    """Updates/Creates one program information

    see
    https://github.com/SchedulesDirect/JSON-Service/wiki/API-20141201#download-program-information

    """
    try:
        progid = prog["programID"]
        log.debug(f"addUpdateProg: {progid}")
        eprog = session.query(Program).filter_by(programid=progid).first()
        if eprog:
            log.debug(f"{progid} already exists")
            if eprog.md5 == prog["md5"]:
                log.debug("md5 match")
                return None
            else:
                log.debug(f"md5 mismatch: storing {progid}")
                eprog = setProgData(eprog, prog)
                # db.session.commit()
        else:
            log.debug(f"new program: {progid}")
            kwargs = {"programid": progid, "md5": prog["md5"]}
            kwargs["title"] = extractString(prog["titles"], "title120")
            log.debug(f"title: {kwargs['title']}")
            kwargs["episodetitle"] = (
                "" if "episodeTitle150" not in prog else prog["episodeTitle150"]
            )
            if "descriptions" in prog and "description100" in prog["descriptions"]:
                kwargs["shortdesc"] = extractString(
                    prog["descriptions"]["description100"], "description"
                )
            if "descriptions" in prog and "description1000" in prog["descriptions"]:
                kwargs["longdesc"] = extractString(
                    prog["descriptions"]["description1000"], "description"
                )
            if "originalAirDate" in prog:
                kwargs["originalairdate"] = prog["originalAirDate"]
            else:
                log.debug(f"originalAirDate not in {prog=}")
            if "metadata" in prog:
                kwargs["series"], kwargs["episode"] = extractSeries(prog["metadata"])
            eprog = Program(**kwargs)
            session.add(eprog)
            # db.session.commit()
        if "cast" in prog:
            [addUpdatePerson(item, progid, session) for item in prog["cast"]]
        if "crew" in prog:
            [addUpdatePerson(item, progid, session) for item in prog["crew"]]
    except Exception as e:
        errorExit(sys.exc_info()[2], e)


def setProgData(eprog, prog):
    try:
        eprog.md5 = prog["md5"]
        eprog.title = extractString(prog["titles"], "title120")
        eprog.episodetitle = (
            "" if "episodeTitle150" not in prog else prog["episodeTitle150"]
        )
        if "descriptions" in prog and "description1000" in prog["descriptions"]:
            eprog.longdesc = extractString(
                prog["descriptions"]["description1000"], "description"
            )
        if "descriptions" in prog and "description100" in prog["descriptions"]:
            eprog.shortdesc = extractString(
                prog["descriptions"]["description100"], "description"
            )
        if "originalAirDate" in prog:
            eprog.originalairdate = prog["originalAirDate"]
        if "metadata" in prog:
            eprog.series, eprog.episode = extractSeries(prog["metadata"])
        return eprog
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


def extractString(xlist, key):
    try:
        log.debug(f"extractString: {xlist=}, {key=}")
        for item in xlist:
            if key in item:
                return item[key]
        log.warning(f"{key} not found in {xlist}")
        return None
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


def extractSeries(mdata):
    try:
        series = episode = 0
        for item in mdata:
            series = int(item["Gracenote"]["season"])
            episode = int(item["Gracenote"]["episode"])
        return (series, episode)
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


def addUpdatePerson(person, programid, session):
    try:
        log.debug(f"addUpdatePerson: {person['name']}")
        per = session.query(Person).filter_by(personid=person["personId"]).first()
        if not per:
            log.debug(f"storing person: {person['name']}")
            kwargs = {
                "personid": person["personId"],
                "name": person["name"],
                "nameid": person["nameId"],
            }
            per = Person(**kwargs)
            session.add(per)
            # db.session.commit()
        billingorder = "0" if "billingorder" not in person else person["billingorder"]
        role = "" if "role" not in person else person["role"]
        addUpdatePersonMap(per.personid, programid, role, billingorder, session)
    except Exception as e:
        msg = f"{person=}, {programid=}"
        errorExit(sys.exc_info()[2], e, msg)


def addUpdatePersonMap(personid, programid, role, billingorder, session):
    try:
        cm = (
            session.query(Personmap)
            .filter_by(programid=programid, personid=personid)
            .first()
        )
        if not cm:
            kwargs = {
                "programid": programid,
                "personid": personid,
                "role": role,
                "billingorder": billingorder,
            }
            cm = Personmap(**kwargs)
            session.add(cm)
            # db.session.commit()
    except Exception as e:
        msg = f"{personid=}, {programid=}, {role=}, {billingorder=}"
        errorNotify(sys.exc_info()[2], e, msg)


def updateChannels(linupdata, eng):
    try:
        # with open("/home/chris/tmp/lineups.json", "r") as ifn:
        #     xdict = json.load(ifn)
        # xdict = json.loads(linupdata)
        xdict = linupdata
        rmap = getRMap(xdict["map"])
        labels = ["name", "callsign"]
        llabs = ["height", "width", "category", "md5", "source"]
        existstation = createdstation = 0
        # outer and inner context manager for the Session object
        # the outer `session` opens the session and auto closes it
        # the inner `session.begin` starts transactions and
        # will auto commit when the code drops out of the context manager
        with Session(eng) as session, session.begin():
            for station in xdict["stations"]:
                stationid = int(station["stationID"])
                if (
                    not session.query(Channel)
                    .filter(Channel.stationid == stationid, Channel.getdata > 0)
                    .first()
                ):
                    kwargs = {key: station[key] for key in labels}
                    kwargs["stationid"] = stationid
                    kwargs["channelnumber"] = rmap[stationid]
                    stat = Channel(**kwargs)
                    log.debug(f"Inserting {stat=}")
                    session.add(stat)
                    # db.session.commit()
                    createdstation += 1
                else:
                    existstation += 1
        log.info(
            f"Channels inserted: {createdstation}, Existing Channels: {existstation}"
        )
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


def setMappedChannels(eng, updates):
    try:
        with Session(eng) as session, session.begin():
            for update in updates:
                session.update(update)
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


def mapToDVB(eng, zap):
    try:
        with Session(eng) as session, session.begin():
            chans = session.query(Channel).all()
            for chan in chans:
                if chan.dvbname is not None:
                    continue
                poss, found = searchZap(zap, chan.name)
                if found:
                    print(f"Channel {chan.name} - name found exactly in zap")
                    chan.dvbname = chan.name
                    chan.getdata = chooseGetData(chan.name)
                    continue
                choice = chooseName(poss, chan.name)
                if len(choice) == 0:
                    break
                chan.dvbname = choice.strip()
                print(f"DVB Name {chan.dvbname} set for {chan.name}")
                chan.getdata = chooseGetData(chan.name)
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


def getRMap(xmap):
    try:
        rmap = {}
        for xm in xmap:
            rmap[int(xm["stationID"])] = int(xm["channel"])
        return rmap
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


def whatsOnNow(eng, now=int(time.time()), favs=True, limit=40):
    """
    programid = Column(String(128), primary_key=True)
    stationid = Column(String(128), primary_key=True)
    airdate = Column(Integer(), primary_key=True)
    duration = Column(Integer())
    md5 = Column(String(32))
    """
    try:
        xscheds = []
        xfavs = favourites(eng, favs=favs)
        chanids = [x["stationid"] for x in xfavs]
        timewidth = 3600
        with Session(eng) as session, session.begin():
            if limit > 0:
                scheds = (
                    session.query(Schedule)
                    .filter(
                        Schedule.airdate < (now + timewidth),
                        (Schedule.airdate + Schedule.duration) > now,
                        Schedule.stationid.in_(chanids),
                    )
                    .order_by(Schedule.airdate)
                    .limit(limit)
                )
            else:
                scheds = (
                    session.query(Schedule)
                    .filter(
                        Schedule.airdate < (now + timewidth),
                        (Schedule.airdate + Schedule.duration) > now,
                        Schedule.stationid.in_(chanids),
                    )
                    .order_by(Schedule.airdate)
                    .all()
                )
            for x in scheds:
                dsched = x._todict_()
                dsched["dchan"], dsched["dprog"] = progDetailsFromSchedule(session, x)
                xscheds.append(dsched)
        return xscheds
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


def chanDetails(session, chanid):
    try:
        chan = session.query(Channel).filter_by(stationid=chanid).first()
        dchan = chan._todict_()
        return dchan
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


def progDetailsFromSchedule(session, schedule, withchan=True):
    try:
        # there should only be one program
        prog = session.query(Program).filter_by(programid=schedule.programid).first()
        # print(f"progDetailsFromSchedule: {prog=}")
        dprog = prog._todict_()
        # print(f"progDetailsFromSchedule: {dprog=}")
        dchan = chanDetails(session, schedule.stationid) if withchan else None
        # print(f"progDetailsFromSchedule: {dchan=}")
        return (dchan, dprog)
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


def chanProgs(eng, chanid, now=int(time.time()), limit=40):
    try:
        xscheds = []
        timewidth = 86400
        with Session(eng) as session, session.begin():
            dchan = chanDetails(session, chanid)
            if limit > 0:
                scheds = (
                    session.query(Schedule)
                    .filter(
                        Schedule.stationid == chanid,
                        Schedule.airdate < (now + timewidth),
                        (Schedule.airdate + Schedule.duration) > now,
                    )
                    .order_by(Schedule.airdate)
                    # .limit(limit)
                )
            else:
                scheds = (
                    session.query(Schedule)
                    .filter(
                        Schedule.stationid == chanid,
                        Schedule.airdate < (now + timewidth),
                        (Schedule.airdate + Schedule.duration) > now,
                    )
                    .order_by(Schedule.airdate)
                    .all()
                )
            for x in scheds:
                dsched = x._todict_()
                # print(f"schedules: current: {x=}: {dsched=}")
                _, dsched["dprog"] = progDetailsFromSchedule(session, x, withchan=False)
                dsched["dchan"] = dchan
                xscheds.append(dsched)
        return xscheds
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


def scheduleFromMD5(eng, schedulemd5):
    try:
        with Session(eng) as session, session.begin():
            pid = programFromScheduleMD5(session, schedulemd5)
            return pid
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


def programFromScheduleMD5(session, smd5):
    try:
        sched = session.query(Schedule).filter_by(md5=smd5).first()
        # print(f"programFromScheduleMD5: {sched=}")
        dchan, dprog = progDetailsFromSchedule(session, sched)
        # print(f"programFromScheduleMD5: {dchan=}, {dprog=}")
        dsched = sched._todict_()
        # print(f"programFromScheduleMD5: {dsched=}")
        peeps = personFromProgId(session, dprog["programid"])
        pid = programInfoDict(dsched=dsched, dchan=dchan, dprog=dprog, peeps=peeps)
        # print(f"programFromScheduleMD5: {pid=}")
        return pid
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


def personFromProgId(session, progid):
    try:
        xdats = []
        xdat = None
        peeps = session.query(Personmap).filter_by(programid=progid).all()
        # print(f"personFromProgId: {peeps=}")
        for peep in peeps:
            pdat = session.query(Person).filter_by(personid=peep.personid).first()
            xdat = {
                "name": pdat.name,
                "role": peep.role,
                "billingorder": peep.billingorder,
            }
            # print(f"personFromProgId: {xdat=}")
            xdats.append(xdat)
        return xdats
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


def setScheduleRecord(eng, schedmd5):
    try:
        now = int(time.time())
        with Session(eng) as session, session.begin():
            # sched = session.query(Schedule).filter_by(md5=schedmd5, airdate >= now).first()
            sched = (
                session.query(Schedule)
                .filter(
                    Schedule.md5 == schedmd5,
                    (Schedule.airdate + Schedule.duration) > now,
                )
                .first()
            )
            # print(f"{sched=}")
            if sched is not None:
                sched.record = 1
                # sched["record"] = 1
                session.add(sched)
                return True
        return False
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


def unsetScheduleRecord(eng, sched):
    try:
        with Session(eng) as session, session.begin():
            kwargs = {"md5": sched["md5"], "airdate": sched["airdate"], "record": 1}
            log.debug(f"unsetScheduleRecord: {kwargs = }")
            xsched = session.query(Schedule).filter_by(**kwargs).first()
            log.debug(f"unsetScheduleRecord: {xsched = }")
            xsched.record = 0
            session.commit()
            return True
            # xsched = (
            #     session.query(Schedule)
            #     .filter(
            #         Schedule.md5 == sched["md5"],
            #         Schedule.airdate == sched["airdate"],
            #         Schedule.record == 1,
            #     )
            #     .first()
            # )
            # log.debug(f"{xsched = }")
            # if xsched is not None:
            #     sched.record = 0
            #     session.add(sched)
            #     session.commit()
            #     return True
        return False
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


def getScheduleRecord(eng):
    try:
        now = int(time.time())
        recs = []
        with Session(eng) as session, session.begin():
            scheds = (
                session.query(Schedule)
                .filter(
                    (Schedule.airdate + Schedule.duration) > now,
                    Schedule.record == 1,
                )
                .order_by(Schedule.airdate)
                .all()
            )
            for sched in scheds:
                pid = programFromScheduleMD5(session, sched.md5)
                recs.append(pid)
        return recs
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


def programInfoDict(dsched=None, dchan=None, dprog=None, peeps=None):
    try:
        xd = {
            "schedule": dsched,
            "channel": dchan,
            "program": dprog,
            "people": peeps,
            "starttime": dateTimeString(dsched["airdate"]),
        }
        return xd
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


def addRecording(cfg, eng, nextrec, fqfn, adapter):
    try:
        rid = 0
        sched = nextrec["schedule"]
        prog = nextrec["program"]
        recd = {
            "programid": sched["programid"],
            "start": sched["airdate"],
            "duration": sched["duration"],
            "startpad": cfg.get("startpad"),
            "endpad": cfg.get("endpad"),
            "adapter": adapter,
            "filename": fqfn,
            "size": 0,
            "channel": nextrec["channel"]["name"],
        }
        rec = Recording(**recd)
        with Session(eng) as session, session.begin():
            session.add(rec)
            rid = rec.rid
            session.commit()
        return rid
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


def getLastSize(eng, rid):
    try:
        with Session(eng) as session, session.begin():
            rec = session.query(Recording).filter(Recording.rid == rid).first()
        return rec.size
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


def updateSize(eng, rid, size):
    try:
        with Session(eng) as session, session.begin():
            rec = session.query(Recording).filter(Recording.rid == rid).first()
            rec.size = size
            session.commit()
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)
