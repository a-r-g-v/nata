# under heavy development

nata
===

deployment toolkit for google compute engine

*** [Tutorials and Conspect (japanese)](https://github.com/a-r-g-v/nata/blob/develop/README.ja.md) ***

# command

## Service

```
nata service create <yaml-to-path>
nata service delete <service-name>
nata service list
nata service switch <service-name> <app-name>
nata service rolling <service-name>
```

## App
```
nata app create <yaml-to-path>
nata app list 
nata app delete <app-name>
```

# testing
```
python setup.py test
```

# install
```
python setup.py install
```

