# encoding: utf8
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.expression import extract
from sqlalchemy.orm import backref, relationship, Query
from sqlalchemy import Column, DateTime, Index, Integer, String, Text, Boolean, text, ForeignKey
import datetime


Base = declarative_base()



class ServiceRecord(Base):
    __tablename__ = "service"
    no = Column(Integer, primary_key=True)
    name = Column(String(160), unique=False, nullable=False)
    spec = Column(Text, nullable=False)
    created_date = Column(DateTime, default=datetime.datetime.now(), nullable=False)
    archived_date =Column(DateTime, nullable=True)

    lb = relationship('LbRecord', lazy="joined", uselist=False, backref="service")
    apps = relationship('AppRecord', lazy="joined", uselist=True, backref="service")


class LbRecord(Base):
    __tablename__ = "lb"
    no = Column(Integer, primary_key=True)
    address = Column(String(64), nullable=True)
    created_date = Column(DateTime, default=datetime.datetime.now(), nullable=False)
    archived_date =Column(DateTime, nullable=True)
    enable_https = Column(Boolean, nullable=False, default=False)

    appno = Column(Integer, ForeignKey('app.no'), unique=True, nullable=False)
    serviceno = Column(Integer, ForeignKey('service.no'), unique=True, nullable=False)



class AppRecord(Base):
    __tablename__ = "app"
    no = Column(Integer, primary_key=True)
    name = Column(String(160), unique=False, nullable=False)
    spec = Column(Text, nullable=False)
    zone = Column(String(160), nullable=False)
    created_date = Column(DateTime, default=datetime.datetime.now(), nullable=False)
    archived_date =Column(DateTime, nullable=True)

    serviceno = Column(Integer, ForeignKey('service.no'), nullable=False)

    lb = relationship('LbRecord', lazy="joined", uselist=False, backref="app")
