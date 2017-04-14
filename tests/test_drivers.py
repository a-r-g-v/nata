import unittest
import uuid
import yaml

from . import engine, create_spec
from nata import Session
from nata.mappers import AppMapper, ServiceMapper, LbMapper
from nata.domains import App, Service, Lb, Spec
from nata.records import Base
from nata.resources import LbResource, AppResource
from nata.drivers import *

class DriversTest(unittest.TestCase):

    def setUp(self):
        Session().configure(bind=engine)
        Base.metadata.create_all(engine)


    def test_drivers(self):
        spec = create_spec("nata-test-driver")
        service = Service(name="nata-test-driver", spec=spec)

        app = App(name="nata-test-driver", spec=spec, service=service)
        lb = Lb(name="nata-test-driver", spec=spec, app=app, service=service)

        app_resorces = AppResource(app)
        lb_resorces = LbResource(app, lb)

        app_resorces.create()
        lb_resorces.create()

        import time

        time.sleep(120)
        app_resorces.rolling(lb)

        lb_resorces.delete()
        app_resorces.delete()
