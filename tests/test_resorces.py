import unittest
import uuid
import yaml

from . import engine
from nata import Session
from nata.mappers import AppMapper, ServiceMapper, LbMapper
from nata.domains import App, Service, Lb, Spec
from nata.records import Base
from nata.resources import LbResource, AppResource

class ResorcesTest(unittest.TestCase):

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

    def test_app_and_lb_resorces(self):
        spec = self.spec("nata-test-mapper")
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
