from datetime import datetime
import sys

from ccaerrors import errorNotify, errorRaise, errorExit
from dvbctrl.recorder import Recorder


class MonitorRecorder(Recorder):
    def __init__(self, channel, fqfn, adapter=0, starttime=0, endtime=0):
        try:
            super().__init__(channel, fqfn, adapter=adapter)
            self.starttime = starttime
            self.endtime = endtime
            self.lastsize = 0
            self.completed = False
        except Exception as e:
            errorNotify(sys.exc_info()[2], e)

    def __repr__(self):
        try:
            dt = datetime.fromtimestamp(self.starttime)
            st = dt.strftime("%Y-%m-%d %H:%M:%S")
            dt = datetime.fromtimestamp(self.endtime)
            et = dt.strftime("%Y-%m-%d %H:%M:%S")
            msg = f"<MonitorRecorder({self.channel}, {self.fqfn}"
            msg = f"{msg}, adapter={self.dvbc.adapter}, starttime={st}"
            msg = f"{msg}, endtime={et})>"
            return msg
        except Exception as e:
            errorNotify(sys.exc_info()[2], e)
