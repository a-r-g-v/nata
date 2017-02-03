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

        """
        app_resorces.create()
        lb_resorces.create()
        """
        
        def count_stable_instances(app, lb):
            health_status = get_health_in_backend_service(compute, app.name, lb.name, spec)
            if 'healthStatus' not in health_status:
                raise Exception
            cnt = 0
            for health in health_status['healthStatus']:
                if health['healthState'] == 'HEALTHY':
                    cnt += 1
                else:
                    print 'not stable', health
            return cnt

        def wait_for_stable(app, lb, desire_stable_count):
            while count_stable_instances(app, lb) != desire_stable_count:
                print 'wait some maneged instances until stable... desire: %d' % desire_stable_count
                import time
                time.sleep(3)



        """
        # wait some managed instances until stable
        loop = True 
        while loop:
            loop = False
            result = list_managed_instance(compute, app.name, spec)
            if 'managedInstances' not in result:
                raise Exception
            for instance in result['managedInstances']:
                if instance['currentAction'] != 'NONE':
                    loop = True
                    import time
                    time.sleep(3)
        """

        result = get_health_in_backend_service(compute, app.name, lb.name, spec)
        print result
        desire_stable_count = count_stable_instances(app, lb)
        if 'healthStatus' not in result:
            raise Exception
        for instance in result['healthStatus']:
            wait_for_stable(app, lb, desire_stable_count)
            instance_name = instance['instance'].split('/')[-1]
            print 'target', instance_name
            op = delete_instance(compute, instance_name, app.spec)
            wait_for_operation(compute, spec.project, spec.zone, op["name"])

