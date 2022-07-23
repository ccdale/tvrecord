#
# Copyright (c) 2022, Chris Allison
#
#     This file is part of tvrecorder.
#
#     tvrecorder is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     tvrecorder is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with tvrecorder.  If not, see <http://www.gnu.org/licenses/>.
#
"""SQLAlchemy models for tvrecorder."""
import sys

from ccaerrors import errorNotify
from sqlalchemy import Integer, String, Column, inspect
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Schedulemd5(Base):
    __tablename__ = "schedulemd5"

    md5 = Column(String(32), primary_key=True)
    stationid = Column(String(128), primary_key=True)
    datestr = Column(String(128))
    datets = Column(Integer())
    modified = Column(Integer())

    def __repr__(self):
        return f"<Schedulemd5(md5={self.md5}, stationid={self.stationid}, datestr={self.datestr}, md5={self.md5})>"

    def _todict_(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}


class Schedule(Base):
    __tablename__ = "schedule"

    programid = Column(String(128), primary_key=True)
    stationid = Column(String(128), primary_key=True)
    airdate = Column(Integer(), primary_key=True)
    duration = Column(Integer())
    md5 = Column(String(32))

    def __repr__(self):
        return f"<Schedule(programid={self.programid}, stationid={self.stationid}, airdate={self.airdate}>"

    def _todict_(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}


class Channel(Base):
    __tablename__ = "channel"

    stationid = Column(String(128), primary_key=True)
    name = Column(String(128), primary_key=True)
    channelnumber = Column(Integer(), nullable=True)
    callsign = Column(String(128), nullable=True)
    getdata = Column(Integer(), nullable=True)
    dvbname = Column(String(128), nullable=True)

    def __repr__(self):
        return f"<Channel(stationid={self.stationid}, name={self.name}, dvbname={self.dvbname}>"

    def _todict_(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}


class Program(Base):
    __tablename__ = "program"

    programid = Column(String(128), primary_key=True)
    md5 = Column(String(32), primary_key=True)
    title = Column(String(255))
    originalairdate = Column(String(128))
    episodetitle = Column(String(255), nullable=True)
    shortdesc = Column(String(1024), nullable=True)
    longdesc = Column(String(4096), nullable=True)
    series = Column(Integer(), nullable=True)
    episode = Column(Integer(), nullable=True)

    def __repr__(self):
        return f"<Program(title={self.title}, md5={self.md5}>"

    def _todict_(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}


class Person(Base):
    __tablename__ = "person"

    personid = Column(Integer(), primary_key=True)
    name = Column(String(256), primary_key=True)
    nameid = Column(Integer())

    def __repr__(self):
        return (
            f"<Person(personid={self.personid}, nameid={self.nameid}, name={self.name}>"
        )

    def _todict_(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}


class Personmap(Base):
    __tablename__ = "personmap"

    personid = Column(Integer(), primary_key=True)
    programid = Column(String(128), primary_key=True)
    billingorder = Column(Integer())
    role = Column(String(256))

    def __repr__(self):
        return f"<Personmap(personid={self.personid}, programid={self.programid}, role={self.role}>"

    def _todict_(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}
