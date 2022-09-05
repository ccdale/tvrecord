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
from datetime import datetime, timezone
import sys
import time

from ccaerrors import errorNotify


def cleanString(istring):
    """Replaces 'nasty' chars in strings that could be used as filenames"""
    try:
        remove = "/(){}@~!£$%^&*+='\""
        for i in remove:
            istring = istring.replace(i, "")
        istring = istring.replace(" ", "_")
        while "__" in istring:
            istring = istring.replace("__", "_")
        while "--" in istring:
            istring = istring.replace("--", "-")
        istring = istring.replace("_-_", "-")
        istring = istring.replace("-_-", "_")
        return istring
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


def timeString(ts):
    try:
        # tm = time.localtime(ts)
        # xstr = f"{tm.tm_hour:>2}:{tm.tm_min:0>2}"
        dt = datetime.fromtimestamp(ts)
        xdt = dt.replace(tzinfo=timezone.utc).astimezone(tz=None)
        xstr = f"{xdt.hour:>2}:{xdt.minute:0>2}"
        return xstr
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


def dateTimeString(ts):
    try:
        return time.strftime("%c", ts)
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


def durationString(duration):
    try:
        day = int(duration / 86400)
        duration = int(duration % 86400)
        hour = int(duration / 3600)
        duration = int(duration % 3600)
        minute = int(duration / 60)
        second = int(duration % 60)
        if day > 0:
            return f"{day:>2}:{hour:>2}:{minute:0>2}"
        return f"{hour:>2}:{minute:0>2}"
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)
