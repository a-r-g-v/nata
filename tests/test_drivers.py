import unittest
import uuid
import yaml

from . import engine
from nata import Session
from nata.mappers import AppMapper, ServiceMapper, create_session, LbMapper
from nata.domains import App, Service, Lb, Spec
from nata.records import Base
from nata.resources import LbResource, AppResource
from nata.drivers import *

class DriversTest(unittest.TestCase):

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

    def test_drivers(self):
        spec = self.spec("push7-test-driver")
        service = Service(name="push7-test-driver", spec=spec)

        app = App(name="push7-test-driver", spec=spec, service=service)
        lb = Lb(name="push7-test-driver", spec=spec, app=app, service=service)

        app_resorces = AppResource(app)
        lb_resorces = LbResource(app, lb)

        app_resorces.create()
        lb_resorces.create()

        import time

        time.sleep(30)
        app_resorces.rolling(lb)

        lb_resorces.delete()
        app_resorces.delete()
