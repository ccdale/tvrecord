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
"""Updated DB module for tvrecord."""
import os
import sys

from ccaerrors import errorNotify, errorExit
import ccalogging

from tvrecord import __version__, appname
from tvrecord.credential import getSDCreds
from tvrecord.config import Configuration
from tvrecord.tvrecorddb.db import makeDBEngine
from tvrecord.tvrecorddb.wrangler import updateChannels, schedules
from tvrecord.tvrecordsd.sdapi import SDApi

home = os.path.expanduser("~/")
logd = os.path.join(home, "log")
res = os.makedirs(logd, exist_ok=True)
logfn = os.path.join(logd, f"{appname}.log")
ccalogging.setLogFile(logfn, rotation=30)
ccalogging.setInfo()
log = ccalogging.log


def linupRefresh(sd, cf, eng, force=False):
    try:
        for lineup in sd.lineups:
            if sd.getTimeStamp(lineup["modified"]) > cf.get("lineupdate", 0) or force:
                log.info(f"Lineup changes detected: refreshing lineup {lineup}")
                lineupdata = sd.getLineup(lineup["lineup"])
                updateChannels(lineupdata, eng)
                cf.set("lineupdate", sd.getTimeStamp(lineup["modified"]))
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


def begin(appname, debug=False):
    try:
        cf = Configuration(appname=appname)
        mysqleng = makeDBEngine(cf, echo=debug)
        uname, pword, token, tokenexpires = getSDCreds(cf)
        if tokenexpires is None:
            tokenexpires = 0
        kwargs = {
            "username": uname,
            "password": pword,
            "appname": appname,
            "token": token,
            "tokenexpires": tokenexpires,
            "debug": debug,
        }
        sd = SDApi(**kwargs)
        sd.apiOnline()
        if not sd.online:
            raise Exception("Schedules Direct does not appear to be online.")
        return (cf, sd, mysqleng)
    except Exception as e:
        errorExit(sys.exc_info()[2], e)


def close(cf, sd):
    try:
        cf.set("token", sd.token)
        cf.set("tokenexpires", sd.tokenexpires)
        cf.writeConfig()
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


def updatedb(debug=False):
    try:
        log.info(f"{appname} {__version__} database updater starting.")
        cf, sd, mysqleng = begin(appname, debug=debug)
        linupRefresh(sd, cf, mysqleng)
        schedules(sd, mysqleng)
        close(cf, sd)
        log.info(f"{appname} database updater completed.")
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


if __name__ == "__main__":
    updatedb()
