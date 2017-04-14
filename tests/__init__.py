
import os

os.environ['NATA_SCHEMA'] = 'sqlite://'

from nata.config import config
from nata import init_engine
from nata.domains import Spec

engine = init_engine()

def create_spec(name="nata-test"):
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
  requestPath: /api/v1
  checkIntervalSec: 3
  timeoutSec: 3
LBtimeoutSec: 100
        """.format(name=name))
