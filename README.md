# nata
deployment toolkit for google compute engine

# service yaml
```yaml
---

name: test2
project: poe
zone: asia-northeast1-a
image: global/images/poe-1234
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


```


# command
```
nata app create <yaml-name>
nata app list 
nata app delete <app-name>
nata service create <yaml-name>
nata service delete <lb-name>
nata service list
nata service use <app-name>
```

# testing
```
python setup.py test
```

# install
```
python setup.py install
```

