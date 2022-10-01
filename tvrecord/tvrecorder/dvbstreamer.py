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
"""dvbstreamer module"""
import sys

from ccaerrors import errorNotify

from tvrecord.tvrecorder.shell import shellCommand


class DvbStreamer:
    """dvbstreamer daemon class."""

    def __init__(self, adaptor=0, ip="localhost", user="dvbctrl", passw="dvbctrl"):
        try:
            self.adaptor = adaptor
            self.ip = ip
            self.user = user
            self.passw = passw
            self.pid = None
        except Exception as e:
            errorNotify(sys.exc_info()[2], e)

    def start(self):
        """starts the dvbstreamer on this adaptor

        Usage:dvbstreamer <options>
            Options:
            -v            : Increase the amount of debug output, can be used multiple
                            times for more output
            -L <file>     : Set the location of the log file.
            -V            : Print version information then exit
            -o <mrl>      : Output primary service to the specified mrl.
            -a <adapter>  : Use adapter number (ie /dev/dvb/adapter<adapter>/...)
            -f <file>     : Run startup script file before starting the command prompt
            -d            : Run as a daemon.
            -R            : Use hardware PID filters, only 1 service filter supported.
            -I            : Force use of ISDB-T delivery system

            Remote Interface Options
            -r            : Start remote interface as well as console shell.
            -D            : Start remote interface but disable console shell.
            -u <username> : Username used to login remotely to control this instance.
            -p <password> : Password used to login remotely to control this instance.
            -n <name>     : Informational name for this instance.
            -i <address>  : IP address to bind to.
        """
        try:
            cmd = f"dvbstreamer -dD -a {self.adaptor} -i {self.ip} -u {self.user} -p {self.passw}"
            txt, err = shellCommand(cmd)
        except Exception as e:
            errorNotify(sys.exc_info()[2], e)

    def stop(self):
        try:
            pass
        except Exception as e:
            errorNotify(sys.exc_info()[2], e)
