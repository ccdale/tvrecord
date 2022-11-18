import datetime
import re

from tvrecord.tvrecorder.monitor import makeTs


class PytestRegex:
    """Assert that a given string matches the regular expression"""

    def __init__(self, pattern, flags=0):
        self._regex = re.compile(pattern, flags)

    def __eq__(self, teststr):
        return bool(self._regex.match(teststr))

    def __repr__(self):
        return self._regex.pattern


def test_makeTs():
    ts = makeTs()
    assert ts == PytestRegex("[0-9]{14}")


def test_makeTs_defined_input():
    args = [2019, 2, 14, 21, 4, 28]
    dt = datetime.datetime(*args)
    nstr = "".join([f"{x:02}" for x in args])
    ts = makeTs(dt)
    assert ts == nstr
