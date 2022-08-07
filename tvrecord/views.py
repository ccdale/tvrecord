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
from urllib.parse import quote_plus

from ccaerrors import errorNotify
from flask import render_template

from tvrecord import app, cf, eng
from tvrecord.html import mkCellDict
from tvrecord.strings import durationString, timeString
from tvrecord.tvrecorddb.wrangler import (
    chanProgs,
    favourites,
    whatsOnNow,
    scheduleFromMD5,
)

# from tvrecord.tvrecorddb.wrangler import whatsOnNow


@app.route("/")
def index():
    try:
        # op = "Hello world"
        # op = whatsOnNowTable(eng)
        headings = ["Channel", "Start", "Duration", "Title", "Description"]
        lines = []
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
            lines.append(line)
            # print(lines)
        return render_template("index.html", headings=headings, lines=lines)
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


@app.route("/channel/<chanid>")
def channel(chanid):
    try:
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
            lines.append(line)
        return render_template(
            "channel.html", headings=headings, lines=lines, cname=cname
        )
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


@app.route("/channels/<fav>")
def channels(fav):
    try:
        favs = True if fav == "1" else False
        chans = favourites(eng, favs=favs)
        return render_template("channels.html", chans=chans, fav=fav)
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


@app.route("/program/<schedulemd5>")
def program(schedulemd5):
    try:
        dsched, dchan, dprog, peeps = scheduleFromMD5(eng, schedulemd5)
        return render_template(
            "program.html", dsched=dsched, dchan=dchan, dprog=dprog, peeps=peeps
        )
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)
