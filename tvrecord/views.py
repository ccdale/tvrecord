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

from ccaerrors import errorNotify
from flask import render_template

from tvrecord import app, cf, eng
from tvrecord.html import whatsOnNowTable, channelProgsTable, mkCellDict
from tvrecord.strings import durationString, timeString
from tvrecord.tvrecorddb.wrangler import favourites, whatsOnNow

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
            line = [mkCellDict(won["dchan"]["name"], "cname")]
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
            print(lines)
        return render_template("index.html", headings=headings, lines=lines)
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


@app.route("/channel/<chanid>")
def channel(chanid):
    try:
        op = channelProgsTable(eng, chanid)
        return op
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


@app.route("/channels")
def channels():
    try:
        chans = favourites(eng)
        return render_template("channels.html", chans=chans)
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)
