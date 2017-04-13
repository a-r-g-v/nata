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

    def spec(self, name="nata-test"):
        return Spec(yaml="""
---
name: {name}
project: nata-jp
zone: asia-northeast1-a
properties:
  - machineType: g1-small
    canIpForward: True
    disks: 
      - boot: True
        autoDelete: True
        deviceName: {name}
        initializeParams:
          - sourceImage: global/images/family/nata-sampleapp
            diskSizeGb: 10
    networkInterfaces:
      - network: global/networks/default
        accessConfigs:
          - name: external-IP
            type: ONE_TO_ONE_NAT
    scheduling:
      preemptible: True
autoscalingPolicy:
  maxNumReplicas: 10
  minNumRreplicas: 1
  coolDownPeriodSec: 60
  cpuUtilization:
    utilizationTarget: 0.9
enableCDN: False
httpHealthCheck:
  requestPath: /api/v1/
  checkIntervalSec: 3
  timeoutSec: 3
LBtimeoutSec: 100
        """.format(name=name))

    def test_drivers(self):
        spec = self.spec("nata-test-driver")
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
