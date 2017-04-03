import unittest
import uuid
import yaml

from . import engine
from nata import Session
from nata.mappers import AppMapper, ServiceMapper, create_session, LbMapper
from nata.domains import App, Service, Lb, Spec
from nata.records import Base



class MappersTest(unittest.TestCase):

    def setUp(self):
        Session().configure(bind=engine)
        Base.metadata.create_all(engine)

    def spec(self, name="nata-test"):
        return Spec(yaml="""
---
name: {name}
project: nata-jp
zone: asia-northeast1-a
image: global/images/family/nata-sampleapp-master
diskSizeGb: 10
machineType: n1-standard-1
networkInterfaces:
  - network: global/networks/default
    accessConfigs:
      - name: external-IP
        type: ONE_TO_ONE_NAT
autoscalingPolicy:
  maxNumReplicas: 10
  minNumRreplicas: 1
  coolDownPeriodSec: 60
  cpuUtilization:
    utilizationTarget: 0.9
enableCDN: False
autoDelete: True
        """.format(name=name))

    def test_service_crud(self):
        spec = self.spec()
        service = Service(name="nata-test", spec=spec)

        # Insert
        ServiceMapper.insert(service)
        names = [s.name for s in ServiceMapper.list()]
        assert service.name in names


        # Get
        get_service = ServiceMapper.get('nata-test')
        assert get_service.name == service.name
        assert type(get_service) is Service

        # Update
        service.spec.test_update = True
        ServiceMapper.update(service)
        get_service = ServiceMapper.get('nata-test')
        assert get_service.spec.test_update is True

        # Delete
        ServiceMapper.delete(service)
        names = [s.name for s in ServiceMapper.list()]
        assert service.name not in names

    def test_app_crud(self):
        spec = self.spec()

        service = Service(name="nata-test2", spec=spec)
        ServiceMapper.insert(service)
        names = [s.name for s in ServiceMapper.list()]
        assert service.name in names

        app = App(name="nata-test2", spec=spec, service=service)

        # Insert
        AppMapper.insert(app)
        names = [s.name for s in AppMapper.list()]
        assert app.name in names

        get_service = ServiceMapper.get(service.name)
        assert app in get_service.apps

        # Get
        get_app = AppMapper.get('nata-test2')
        assert get_app.name == app.name
        assert type(get_app) is App

        # Update
        app.spec.test_update = True
        AppMapper.update(app)
        get_app = AppMapper.get('nata-test2')
        assert get_app.spec.test_update is True

        # Delete
        AppMapper.delete(app)
        names = [s.name for s in AppMapper.list()]
        assert app.name not in names
        ServiceMapper.delete(service)

    def test_lb_crud(self):
        spec = self.spec("nata-test3")


        service = Service(name="nata-test3", spec=spec)
        ServiceMapper.insert(service)
        names = [s.name for s in ServiceMapper.list()]
        assert service.name in names

        app = App(name="nata-test3", spec=spec, service=service)
        AppMapper.insert(app)
        names = [s.name for s in AppMapper.list()]
        assert app.name in names


        lb = Lb(name="nata-test3", spec=spec, app=app, service=service)
        # Insert
        LbMapper.insert(lb)
        names = [s.name for s in LbMapper.list()]
        assert lb.name in names

        get_service = ServiceMapper.get(service.name)
        assert lb == get_service.lb

        # Get
        get_lb = LbMapper.get('nata-test3')
        assert get_lb.name == lb.name
        assert type(get_lb) is Lb

        get_lb.address = "test"

        #Update
        LbMapper.update(get_lb)

        # Get
        get_updated_lb = LbMapper.get('nata-test3')
        assert get_updated_lb.name == lb.name
        assert type(get_updated_lb) is Lb
        assert get_updated_lb.address == "test"


        # Delete
        LbMapper.delete(lb)
        names = [s.name for s in LbMapper.list()]
        assert lb.name not in names
        ServiceMapper.delete(service)
