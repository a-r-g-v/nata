Example Application for nata
===

# Image Build

First, nata users should be prepared image of google compute engine.  
You can build the image for nata using packer.

```
packer build ./packer.json
```



Next, nata users should be prepared spec yaml file that includes provisioning and configuration plan. 

See below for example of the spec yaml file.

```
name: test-app
project: nata-jp
zone: asia-northeast1-a
properties:
  - machineType: g1-small
    canIpForward: True
    disks: 
      - boot: True
        autoDelete: True
        deviceName: test-app
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
```
