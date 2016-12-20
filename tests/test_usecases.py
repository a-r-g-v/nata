import unittest
import uuid
import yaml

from . import engine
from nata import Session
from nata.mappers import AppMapper, ServiceMapper, create_session, LbMapper
from nata.domains import App, Service, Lb, Spec
from nata.records import Base
from nata.resources import LbResource, AppResource
from nata.usecases import app_factory, lb_factory, ServiceUseCase, AppUseCase

class UsecaseTest(unittest.TestCase):

    def setUp(self):
        Session().configure(bind=engine)
        Base.metadata.create_all(engine)

    def spec(self, name="push7-test-usecase"):
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


    def test_app_lb_factory(self):
        spec = self.spec('push7-test-app')
        service = Service('push7-test-app', spec)
        ServiceMapper.insert(service)

        new_app = app_factory('push7-test-app', spec, service)
        assert new_app.name == 'push7-test-app'

        names = [ app.name for app in AppMapper.list()]
        assert 'push7-test-app' in names

        new_lb = lb_factory('push7-test-app', spec, new_app, service)
        assert new_lb.name == 'push7-test-app'


        lb_r = LbResource(new_lb, new_app)
        app_r = AppResource(new_app)

        lb_r.delete()
        app_r.delete()
        assert lb_r.exist() is False
        assert app_r.exist() is False
    
    def test_service(self):
        spec = self.spec('push7-test-service-uc')

        ServiceUseCase.create(spec)
        names = [ service.name for service in ServiceUseCase.list()]
        assert 'push7-test-service-uc' in names

        def search_app(name='push7-test-service-uc'):
            apps = []
            for app in AppUseCase.list():
                if name in app.name:
                    apps.append(app)
            if len(apps) == 0:
                return None
            return apps

        assert search_app() is not None

        import ptpdb; ptpdb.set_trace()

        AppUseCase.create(spec)

        target = None
        for app in search_app():
            if not app.primary:
                target = app
        
        ServiceUseCase.switch('push7-test-service-uc', target.name)

        target2 = None
        for app in search_app():
            if app.primary:
                target2 = app

        assert target2 == target


        ServiceUseCase.delete('push7-test-service-uc')
        names = [ service.name for service in ServiceUseCase.list()]
        assert 'push7-test-service-uc' not in names


        assert search_app() is None



    def test_app(self):
        spec = self.spec('push7-test-app-uc')

        service = Service('push7-test-app-uc', spec)
        ServiceMapper.insert(service)

        AppUseCase.create(spec)
        target = None
        for app in AppUseCase.list():
            if 'push7-test-app-uc' in app.name:
                target = app

        assert target is not None

        AppUseCase.delete(app.name)
        names = [ app.name for app in AppUseCase.list()]

        booleans = [ 'push7-test-app-uc' in app.name for app in AppUseCase.list()]
        assert True not in booleans
        ServiceMapper.delete(service)
