import unittest
import uuid
import yaml

from . import engine, create_spec
from nata import Session
from nata.mappers import AppMapper, ServiceMapper, LbMapper
from nata.domains import App, Service, Lb, Spec
from nata.records import Base
from nata.resources import LbResource, AppResource
from nata.usecases import app_factory, lb_factory, ServiceUseCase, AppUseCase

class UsecaseTest(unittest.TestCase):

    def setUp(self):
        Session().configure(bind=engine)
        Base.metadata.create_all(engine)


    def test_app_lb_factory(self):
        spec = create_spec('nata-test-app')
        service = Service('nata-test-app', spec)
        ServiceMapper.insert(service)

        new_app = app_factory('nata-test-app', spec, service)
        assert new_app.name == 'nata-test-app'

        names = [ app.name for app in AppMapper.list()]
        assert 'nata-test-app' in names

        new_lb = lb_factory('nata-test-app', spec, new_app, service)
        assert new_lb.name == 'nata-test-app'


        lb_r = LbResource(new_lb, new_app)
        app_r = AppResource(new_app)

        lb_r.delete()
        app_r.delete()
        assert lb_r.exist() is False
        assert app_r.exist() is False
    
    def test_service(self):
        spec = create_spec('nata-test-service-uc')

        ServiceUseCase.create(spec)
        names = [ service.name for service in ServiceUseCase.list()]
        assert 'nata-test-service-uc' in names

        def search_app(name='nata-test-service-uc'):
            apps = []
            for app in AppUseCase.list():
                if name in app.name:
                    apps.append(app)
            if len(apps) == 0:
                return None
            return apps

        assert search_app() is not None


        AppUseCase.create(spec)

        target = None
        for app in search_app():
            if not app.primary:
                target = app
        
        ServiceUseCase.switch('nata-test-service-uc', target.name)

        target2 = None
        for app in search_app():
            if app.primary:
                target2 = app

        assert target2 == target


        ServiceUseCase.delete('nata-test-service-uc')
        names = [ service.name for service in ServiceUseCase.list()]
        assert 'nata-test-service-uc' not in names


        assert search_app() is None



    def test_app(self):
        spec = create_spec('nata-test-app-uc')

        service = Service('nata-test-app-uc', spec)
        ServiceMapper.insert(service)

        AppUseCase.create(spec)
        target = None
        for app in AppUseCase.list():
            if 'nata-test-app-uc' in app.name:
                target = app

        assert target is not None

        AppUseCase.delete(app.name)
        names = [ app.name for app in AppUseCase.list()]

        booleans = [ 'nata-test-app-uc' in app.name for app in AppUseCase.list()]
        assert True not in booleans
        ServiceMapper.delete(service)
