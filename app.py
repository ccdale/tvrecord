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
"""app module for tvrecord."""
import os
import sys

from ccaerrors import errorNotify, errorExit

# set to development for debugging
# before importing tvrecord

# os.environ["FLASK_ENV"] = "development"
os.environ["FLASK_ENV"] = "nosqldebug"

import tvrecord

# print(f"config: {tvrecord.cf=}")

# setup is now all in the package module __init__.py
# the necessary connections to the config and the db
# are now tvrecord.cf and tvrecord.eng
# run the flask server
tvrecord.app.run(host="0.0.0.0")
