# encoding: utf-8
from .domains import Service, App, Lb, Spec
from .records import Base, ServiceRecord, AppRecord, LbRecord
from .config import config
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.orm.query import Query
from sqlalchemy import create_engine
from sqlalchemy.sql import column
from datetime import datetime
import threading
import abc
import json


def create_session(engine):
    local = threading.local()
    def get_session():
        if hasattr(local, 'session'):
            return local.session
        local.session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
        return local.session
    return get_session

def init_engine(echo=False):
    return create_engine(config['schema'], encoding='utf-8', echo=echo)

class MapperBase(object):
    __metaclass__ = abc.ABCMeta

    @classmethod
    def get_session(cls):
        from . import Session
        return Session()

    @classmethod
    def query(cls, record):
        return cls.get_session().query(record).filter(record.archived_date == None)

    @classmethod
    def services(cls):
        return cls.query(ServiceRecord)

    @classmethod
    def apps(cls):
        return cls.query(AppRecord)

    @classmethod
    def lbs(cls):
        return cls.query(LbRecord)

class ServiceMapper(MapperBase):

    @classmethod
    def convert_record_to_domain(cls, service_record):
        spec = Spec(spec=json.loads(service_record.spec))
        service =  Service(service_record.name, spec)
        if service_record.apps is not None or len(service_record.apps) > 0:
            for app_record in service_record.apps:
                service.set_app(AppMapper.convert_record_to_domain(app_record, service=service))

        if service_record.lb is not None:
            service.set_lb(LbMapper.convert_record_to_domain(service_record.lb, service=service))

        return service


    @classmethod
    def get(cls, service_name):
        service_record = cls.services().filter_by(name=service_name).first()
        if service_record is not None:
            return cls.convert_record_to_domain(service_record)

    @classmethod
    def list(cls):
        results = []
        service_records = cls.services().all()
        for service_record in service_records:
            results.append(cls.convert_record_to_domain(service_record))
        return results

    @classmethod
    def delete(cls, service):
        service_record = cls.services().filter_by(name=service.name).first()
        session = cls.get_session()
        now = datetime.now()
        if service_record.apps is not None and len(service_record.apps) > 0:
            for app in service_record.apps :
                app.archived_date = now
                session.add(app)
        if service_record.lb is not None:
            service_record.lb.archived_date = now
            session.add(service_record.lb)
        service_record.archived_date = now
        session.add(service_record)
        session.commit()

    @classmethod
    def insert(cls, service):
        spec = spec=service.spec.to_json()
        service_record = ServiceRecord(name=service.name, spec=spec)
        session = cls.get_session()
        session.add(service_record)
        session.commit()

    @classmethod
    def update(cls, service):
        service_record = cls.services().filter_by(name=service.name).first()
        for (key, value) in service.__dict__.items():
            if '__' in key or 'no' in key or 'name' in key:
                continue

            if key == 'spec' and 'spec' in service_record.__dict__:
                service_record.spec = value.to_json()

            elif key == "apps":
                for app in value:
                    app.service = service
                    AppMapper.update(app)

            elif key == "lb":
                if value is None:
                    continue
                value.service = service
                LbMapper.update(value)


            elif key in service_record.__dict__:
                service_record.__setattr__(key, value)

        session = cls.get_session()
        session.add(service_record)
        session.commit()



class AppMapper(MapperBase):

    @classmethod
    def convert_record_to_domain(cls, app_record, service=None):
        spec = Spec(spec=json.loads(app_record.spec))
        if service is None:
            service = ServiceMapper.convert_record_to_domain(app_record.service)
        app = App(app_record.name, spec, service)
        if app_record.lb is not None:
            app.primary = True
        return app

    @classmethod
    def get(cls, app_name):
        app_record = cls.apps().filter_by(name=app_name).first()
        if app_record is not None:
            return cls.convert_record_to_domain(app_record)

    @classmethod
    def list(cls):
        results = []
        app_records = cls.apps().all()
        for app_record in app_records:
            results.append(cls.convert_record_to_domain(app_record))
        return results


    @classmethod
    def delete(cls, app):
        """
        if app.primary:
            raise Exception('primary app cannot be deleted by mapper.')
        """

        app_record = cls.apps().filter_by(name=app.name).first()
        session = cls.get_session()
        app_record.archived_date = datetime.now()
        session.add(app_record)
        session.commit()

    @classmethod
    def insert(cls, app):
        spec = app.spec.to_json()
        service_record = cls.services().filter_by(name=app.service.name).first()
        app_record = AppRecord(name=app.name, spec=spec, zone=app.spec.zone, serviceno=service_record.no)
        session = cls.get_session()
        session.add(app_record)
        session.commit()

    @classmethod
    def update(cls, app):
        app_record = cls.apps().filter_by(name=app.name).first()
        for (key, value) in app.__dict__.items():
            if '__' in key or 'no' in key or 'name' in key:
                continue

            if key == 'spec' and 'spec' in app_record.__dict__:
                app_record.spec = value.to_json()

            elif key == "service":
                serviceno = cls.services().filter_by(name=value.name).first().no
                app_record.serviceno = serviceno

            elif key in ['primary']:
                continue

            elif key in app_record.__dict__:
                app_record.__setattr__(key, value)

        session = cls.get_session()
        session.add(app_record)
        session.commit()
        

class LbMapper(MapperBase):
    @classmethod
    def convert_record_to_domain(cls, lb_record, service=None):
        spec = Spec(spec=json.loads(lb_record.service.spec))
        if service is None:
            service = ServiceMapper.convert_record_to_domain(lb_record.service)
        app = AppMapper.convert_record_to_domain(lb_record.app, service=service)
        lb = Lb(spec.name, spec, app, service)
        lb.address = lb_record.address
        return lb

    @classmethod
    def get(cls, lb_name):
        serviceno = cls.services().filter_by(name=lb_name).first().no
        lb_record = cls.lbs().filter_by(serviceno=serviceno).first()
        if lb_record is not None:
            return cls.convert_record_to_domain(lb_record)

    @classmethod
    def list(cls):
        results = []
        lb_records = cls.lbs().all()
        for lb_record in lb_records:
            results.append(cls.convert_record_to_domain(lb_record))
        return results


    @classmethod
    def delete(cls, lb):
        serviceno = cls.services().filter_by(name=lb.service.name).first().no
        lb_record = cls.lbs().filter_by(serviceno=serviceno).first()
        session = cls.get_session()
        lb_record.archived_date = datetime.now()
        session.add(lb_record)
        session.commit()

    @classmethod
    def insert(cls, lb):
        spec = lb.spec.to_json()
        serviceno = cls.services().filter_by(name=lb.service.name).first().no
        appno = cls.apps().filter_by(name=lb.app.name).first().no
        lb_record = LbRecord(appno=appno, serviceno=serviceno)
        session = cls.get_session()
        session.add(lb_record)
        session.commit()


    @classmethod
    def update(cls, lb):
        serviceno = cls.services().filter_by(name=lb.name).first().no
        lb_record = cls.lbs().filter_by(serviceno=serviceno).first()
        for (key, value) in lb.__dict__.items():
            if '__' in key or 'no' in key or 'name' in key:
                continue

            elif key == "service":
                serviceno = cls.services().filter_by(name=value.name).first().no
                lb_record.serviceno = serviceno

            elif key == "app":
                appno = cls.apps().filter_by(name=value.name).first().no
                lb_record.appno = appno

            elif key in lb_record.__dict__:
                lb_record.__setattr__(key, value)

        session = cls.get_session()
        session.add(lb_record)
        session.commit()

