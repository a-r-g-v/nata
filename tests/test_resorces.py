import unittest
import uuid
import yaml

from . import engine, create_spec
from nata import Session
from nata.mappers import AppMapper, ServiceMapper, LbMapper
from nata.domains import App, Service, Lb, Spec
from nata.records import Base
from nata.resources import LbResource, AppResource

class ResorcesTest(unittest.TestCase):

    def setUp(self):
        Session().configure(bind=engine)
        Base.metadata.create_all(engine)


    def test_app_and_lb_resorces(self):
        spec = create_spec("nata-test-mapper")
        service = Service(name="nata-test-mapper", spec=spec)

        app = App(name="nata-test-mapper", spec=spec, service=service)
        lb = Lb(name="nata-test-mapper", spec=spec, app=app, service=service)

        lb_resorces = LbResource(app, lb)
        app_resorces = AppResource(app)

        assert app_resorces.exist() is False
        app_resorces.create()
        assert app_resorces.exist() is True

        assert lb_resorces.exist() is False
        lb_resorces.create()
        assert lb_resorces.exist() is True
        lb_resorces.delete()
        assert lb_resorces.exist() is False

        app_resorces.delete()
        assert app_resorces.exist() is False
