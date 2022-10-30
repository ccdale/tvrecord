#
# Copyright (c) 2021, Christopher Allison
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
"""Credential object using the system keyring."""
import hashlib
import keyring
import sys

from ccaerrors import errorNotify


def getSDCreds(cf):
    try:
        uname = cf.get("username")
        if uname is None:
            uname = input("Schedules Direct username? >")
            cf.update("username", uname)
        pword = cf.get("password")
        if pword is None:
            xpass = input("SD password? >")
            pword = hashlib.sha1(xpass.encode()).hexdigest()
            cf.set("password", pword)
        return (uname, pword, cf.get("token"), cf.get("tokenexpires"))
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


class Credential:
    def __init__(self, username, host):
        try:
            self.username = username
            self.host = host
        except Exception as e:
            errorNotify(sys.exc_info()[2], e)

    def setPassword(self, password=""):
        try:
            keyring.set_password(self.host, self.username, password)
        except Exception as e:
            errorNotify(sys.exc_info()[2], e)

    def getPassword(self):
        try:
            return keyring.get_password(self.host, self.username)
        except Exception as e:
            errorNotify(sys.exc_info()[2], e)
