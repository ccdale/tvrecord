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
"""db module for tvrecord"""
import sys

from ccaerrors import errorNotify, errorExit
from sqlalchemy import create_engine

from tvrecord.config import Configuration
from tvrecord.tvrecorddb.models import Base


def makeDBCreds(cf):
    try:
        keys = ["dbhost", "dbdb", "dbuser", "dbpass"]
        op = {}
        for key in keys:
            val = cf.get(key)
            if val is None:
                raise Exception(f"setting {key} not found in configuration")
            op[key] = val
        return op
    except Exception as e:
        errorExit(sys.exc_info()[2], e)


def makeDBEngine(cf, echo=False):
    try:
        creds = makeDBCreds(cf)
        connstr = f'mysql+pymysql://{creds["dbuser"]}:{creds["dbpass"]}'
        connstr += f'@{creds["dbhost"]}/{creds["dbdb"]}'
        return create_engine(connstr, echo=echo)
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


def createTables(engine):
    try:
        Base.metadata.create_all(engine)
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


if __name__ == "__main__":
    cf = Configuration(appname="tvrecord")
    mysqleng = makeDBEngine(cf)
    createTables(mysqleng)
