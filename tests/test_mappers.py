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

    def spec(self, name="push7-test"):
        return Spec(yaml="""
---
name: {name}
project: push7-jp
zone: asia-northeast1-a
image: global/images/family/infra-sampleapp-master
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
        service = Service(name="push7-test", spec=spec)

        # Insert
        ServiceMapper.insert(service)
        names = [s.name for s in ServiceMapper.list()]
        assert service.name in names


        # Get
        get_service = ServiceMapper.get('push7-test')
        assert get_service.name == service.name
        assert type(get_service) is Service

        # Update
        service.spec.test_update = True
        ServiceMapper.update(service)
        get_service = ServiceMapper.get('push7-test')
        assert get_service.spec.test_update is True

        # Delete
        ServiceMapper.delete(service)
        names = [s.name for s in ServiceMapper.list()]
        assert service.name not in names

    def test_app_crud(self):
        spec = self.spec()

        service = Service(name="push7-test2", spec=spec)
        ServiceMapper.insert(service)
        names = [s.name for s in ServiceMapper.list()]
        assert service.name in names

        app = App(name="push7-test2", spec=spec, service=service)

        # Insert
        AppMapper.insert(app)
        names = [s.name for s in AppMapper.list()]
        assert app.name in names

        get_service = ServiceMapper.get(service.name)
        assert app in get_service.apps

        # Get
        get_app = AppMapper.get('push7-test2')
        assert get_app.name == app.name
        assert type(get_app) is App

        # Update
        app.spec.test_update = True
        AppMapper.update(app)
        get_app = AppMapper.get('push7-test2')
        assert get_app.spec.test_update is True

        # Delete
        AppMapper.delete(app)
        names = [s.name for s in AppMapper.list()]
        assert app.name not in names
        ServiceMapper.delete(service)

    def test_lb_crud(self):
        spec = self.spec("push7-test3")


        service = Service(name="push7-test3", spec=spec)
        ServiceMapper.insert(service)
        names = [s.name for s in ServiceMapper.list()]
        assert service.name in names

        app = App(name="push7-test3", spec=spec, service=service)
        AppMapper.insert(app)
        names = [s.name for s in AppMapper.list()]
        assert app.name in names


        lb = Lb(name="push7-test3", spec=spec, app=app, service=service)

        # Insert
        LbMapper.insert(lb)
        names = [s.name for s in LbMapper.list()]
        assert lb.name in names

        get_service = ServiceMapper.get(service.name)
        assert lb == get_service.lb

        # Get
        get_lb = LbMapper.get('push7-test3')
        assert get_lb.name == lb.name
        assert type(get_lb) is Lb

        # Delete
        LbMapper.delete(lb)
        names = [s.name for s in LbMapper.list()]
        assert lb.name not in names
        ServiceMapper.delete(service)
