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
"""tvrecorddb package for tvrecord app."""


def searchZap(zap, search):
    try:
        poss = []
        found = False
        sch = search.lower()
        for sect in zap.sections():
            if search.lower()[:4] in sect.lower():
                poss.append(sect)
            elif search == sect:
                found = True
                break
        return (poss, found)
    except Exception as e:
        print(e)
        errorNotify(sys.exc_info()[2], e)


def chooseName(poss, chan):
    try:
        for n in poss:
            print(n)
        print(f"Type the correct DVB name for channel {chan}")
        choice = input("? ")
        return choice
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


def chooseGetData(chan):
    try:
        print(f"0, 1 or 2 - get data for channel {chan}")
        sin = input("? ")
        iin = int(sin)
        if iin < 0 or iin > 2:
            iin = 0
        return iin
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)
