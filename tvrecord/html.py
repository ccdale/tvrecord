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
"""html module for tvrecord."""
import sys

from tvrecord.strings import durationString, timeString
from tvrecord.tvrecorddb.wrangler import whatsOnNow


def mkAttrs(attrs):
    """make html attributes.

    attrs: list of dicts: [{"key":"value"},..]
    returns: str: "key=value key2=value2..."
    """
    try:
        op = ""
        for attr in attrs:
            for key in attr:
                space = " " if len(op) else ""
                op += f"{space}{key}={attr[key]}"
        return op
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


def mkTag(tag, data, attrs=[], newline=True, inlineclose=False):
    try:
        sattrs = mkAttrs(attrs)
        space = " " if len(sattrs) else ""
        nl = "\n" if newline else ""
        if inlineclose:
            op = f"<{tag}{space}{sattrs} />{nl}"
        else:
            op = f"<{tag}{space}{sattrs}>{data}</{tag}{nl}"
        return op
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


def tableHead(heading, attrs=[], newline=True):
    try:
        return mkTag("th", heading, attrs=attrs, newline=newline)
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


def tableCell(data, attrs=[], newline=True):
    try:
        return mkTag("td", data, attrs=attrs, newline=newline)
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


def tableHeadRow(headings, attrs=[], newline=True):
    try:
        h = ""
        for head in headings:
            h += tableHead(head)
        return mkTag("tr", h, attrs=attrs, newline=newline)
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


def tableRow(cells, attrs=[], newline=True):
    """make a Table Row

    cells: list of dicts: [{"cell":data, "attrs": list of dicts},...]
    returns: str
    """
    try:
        row = ""
        for d in cells:
            row += tableCell(d["cell"], attrs=d["attrs"], newline=newline)
        return mkTag("tr", row, attrs=attrs, newline=newline)
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


def mkTable(rows, headings=[], attrs=[], newline=True):
    try:
        r = [tableHeadRow(headings)]
        for row in rows:
            r.append(tableRow(row["cells"], row["attrs"], newline=newline))
        return mkTag("table", "".join(r), attrs=attrs, newline=newline)
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


def whatsOnNowTable(eng):
    try:
        headings = ["Channel", "Start", "Duration", "Title", "Description"]
        wons = whatsOnNow(eng)
        cells = []
        for won in wons:
            line = []
            d = {"cell": won["dchan"]["name"], "attrs": []}
            line.append(d)
            d = {"cell": timeString(won["airdate"]), "attrs": []}
            line.append(d)
            d = {"cell": durationString(won["duration"]), "attrs": []}
            line.append(d)
            d = {"cell": won["dprog"]["title"], "attrs": []}
            line.append(d)
            d = {"cell": won["dprog"]["shortdesc"], "attrs": []}
            line.append(d)
            cells.append(line)
        table = mkTable(cells, headings)
        return table
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)
