#
# Copyright (c) 2022, Christopher Allison
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
"""views module for tvrecord."""
import sys
from urllib.parse import quote_plus, unquote_plus

from ccaerrors import errorNotify
from flask import flash, redirect, render_template, request, url_for

from tvrecord import app, cf, eng
from tvrecord.html import mkCellDict
from tvrecord.strings import durationString, timeString
from tvrecord.tvrecorddb.wrangler import (
    chanProgs,
    favourites,
    whatsOnNow,
    scheduleFromMD5,
    setScheduleRecord,
    getScheduleRecord,
)


@app.route("/")
def index():
    try:
        headings = ["Channel", "Start", "Duration", "Title", "Description", "Record"]
        lines = []
        upcoming = getScheduleRecord(eng)
        wons = whatsOnNow(eng)
        for won in wons:
            chanlink = f"channel/{won['dchan']['stationid']}"
            line = [mkCellDict(won["dchan"]["name"], "cname", chanlink)]
            line.append(mkCellDict(timeString(won["airdate"]), "time"))
            line.append(mkCellDict(durationString(won["duration"]), "time"))
            line.append(mkCellDict(won["dprog"]["title"], "title"))
            desc = (
                won["dprog"]["shortdesc"]
                if won["dprog"]["shortdesc"]
                else won["dprog"]["longdesc"]
            )
            line.append(mkCellDict(desc, "description"))
            line.append(mkCellDict(won["record"], "recordtick", won["md5"]))
            lines.append(line)
        kwargs = {
            "headings": headings,
            "lines": lines,
            "recordurl": url_for("recordProgram"),
            "lenheadings": len(headings),
            "upcoming": upcoming,
            "lenurecs": len(upcoming),
        }
        return render_template("index.html", **kwargs)
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


@app.route("/recordprogram", methods=["POST"])
def recordProgram():
    try:
        data = request.form
        for key in data:
            if key != "submit":
                pinfo = scheduleFromMD5(eng, key)
                setScheduleRecord(eng, key)
                flash(
                    f"{pinfo['program']['title']} set to record on {pinfo['channel']['name']}"
                )
        return redirect(url_for("index"))
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


@app.route("/recordchannelprogram", methods=["POST"])
def recordChannelProgram():
    try:
        data = request.form
        # print(f"form data: {data}")
        for key in data:
            if key not in ["submit", "chanid"]:
                pinfo = scheduleFromMD5(eng, key)
                if setScheduleRecord(eng, key):
                    flash(
                        f"{pinfo['program']['title']} set to record on {pinfo['channel']['name']}"
                    )
                else:
                    flash(
                        f"Failed to set {pinfo['program']['title']} to record on {pinfo['channel']['name']}",
                        "error",
                    )
        return redirect(url_for("channel", chanid=data["chanid"]))
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


@app.route("/channel/<chanid>")
def channel(chanid):
    try:
        upcoming = getScheduleRecord(eng)
        print(f"in channel: chanid is {chanid}")
        # op = channelProgsTable(eng, chanid)
        headings = ["Start", "Duration", "Title", "Description"]
        cprgs = chanProgs(eng, chanid, limit=0)
        cname = cprgs[0]["dchan"]["name"]
        lines = []
        for prg in cprgs:
            line = [mkCellDict(timeString(prg["airdate"]), "time")]
            line.append(mkCellDict(durationString(prg["duration"]), "time"))
            link = f"/program/{quote_plus(prg['md5'])}"
            line.append(mkCellDict(prg["dprog"]["title"], "title", link=link))
            desc = (
                prg["dprog"]["shortdesc"]
                if prg["dprog"]["shortdesc"]
                else prg["dprog"]["longdesc"]
            )
            line.append(mkCellDict(desc, "description"))
            ## todo
            line.append(mkCellDict(prg["record"], "recordtick", prg["md5"]))
            ##
            lines.append(line)
        kwargs = {
            "headings": headings,
            "lines": lines,
            "cname": cname,
            "recordurl": url_for("recordChannelProgram"),
            "chanid": chanid,
            "upcoming": upcoming,
            "lenurecs": len(upcoming),
        }
        return render_template("channel.html", **kwargs)
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


@app.route("/channels/<fav>")
def channels(fav):
    try:
        upcoming = getScheduleRecord(eng)
        favs = True if fav == "1" else False
        chans = favourites(eng, favs=favs)
        kwargs = {
            "chans": chans,
            "fav": fav,
            "upcoming": upcoming,
            "lenurecs": len(upcoming),
        }
        return render_template("channels.html", **kwargs)
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


@app.route("/program/<schedulemd5>")
def program(schedulemd5):
    try:
        schedmd5 = unquote_plus(schedulemd5)
        pinfo = scheduleFromMD5(eng, schedmd5)
        return render_template("program.html", **pinfo)
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)
