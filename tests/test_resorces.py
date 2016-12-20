import unittest
import uuid
import yaml

from . import engine
from nata import Session
from nata.mappers import AppMapper, ServiceMapper, create_session, LbMapper
from nata.domains import App, Service, Lb, Spec
from nata.records import Base
from nata.resources import LbResource, AppResource

class ResorcesTest(unittest.TestCase):

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

    def test_app_and_lb_resorces(self):
        spec = self.spec("push7-test-mapper")
        service = Service(name="push7-test-mapper", spec=spec)

        app = App(name="push7-test-mapper", spec=spec, service=service)
        lb = Lb(name="push7-test-mapper", spec=spec, app=app, service=service)

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
