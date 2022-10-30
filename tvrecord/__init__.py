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
"""package module for tvrecord."""
import os
import sys

from ccaerrors import errorNotify, errorExit
from flask import Flask

from tvrecord.config import Configuration
from tvrecord.tvrecorddb.db import makeDBEngine

# from tvrecord.tvrecorddb.models import Base


def begin(debug=False):
    """Starts a connection to the db and returns the db engine and the app config."""
    try:
        cf = Configuration(appname=appname)
        eng = makeDBEngine(cf, echo=debug)
        return (cf, eng)
    except Exception as e:
        errorExit(sys.exc_info()[2], e)


__version__ = "0.1.9"

appname = "tvrecord"

app = Flask(__name__)
app.secret_key = "a secret key"

debug = True if os.environ.get("FLASK_ENV", "development") == "development" else False
cf, eng = begin(debug=debug)

## circular import warning, don't do anything
# with these views here, just import the file
# as views.py DEPENDS on this __init__.py
# because it uses tvrecord.app!
import tvrecord.views
