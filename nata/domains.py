
class Service(object):

    def __init__(self, name, spec):
        self.name = name
        self.spec = spec
        self.lb = None
        self.apps = []

    def set_app(self, app):
        self.apps.append(app)

    def set_lb(self, lb):
        self.lb = lb

    def get_primary_app(self):
        for app in self.apps:
            if app.primary:
                return app

        raise Exception('primary application is not exist.')

    def __eq__(self, other):
        if other is None or not isinstance(other, Service):
            return False
        return self.name == other.name

    def __ne__(self, other):
        return not self.__eq__(other)


class App(object):

    def __init__(self, name, spec, service):
        self.name = name
        self.spec = spec
        self.primary = False # read only attr
        self.service = service

    @staticmethod
    def generate_name(name):
        import uuid
        return name + uuid.uuid4().hex[0:6]

    def __eq__(self, other):
        if other is None or not isinstance(other, App):
            return False
        return self.name == other.name

    def __ne__(self, other):
        return not self.__eq__(other)

class Lb(object):
    def __init__(self, name, spec, app, service):
        self.name = name
        self.spec = spec
        self.app = app
        self.service = service
        self.address = None

    def __eq__(self, other):
        if other is None or not isinstance(other, Lb):
            return False
        return self.name == other.name

    def __ne__(self, other):
        return not self.__eq__(other)

class Spec(object):

    def __init__(self, spec=None, filename=None, yaml=None):
        if filename is not None:
            import yaml as yam
            self.spec = yam.load(file(filename))
        if yaml is not None:
            import yaml as yam
            self.spec = yam.load(yaml)
        if spec is not None:
            self.spec = spec

    def __getattr__(self, key):
        if key not in self.spec:
            raise AttributeError
        return self.spec[key]

    def __setattr__(self, key, value):
        if key == 'spec':
            self.__dict__['spec'] = value
        else:
            dic = self.__dict__['spec']
            dic[key] = value

    def __delattr__(self, key):
        del self.spec[key]

    def to_json(self):
        import json
        return json.dumps(self.spec)

    def __eq__(self, other):
        if other is None or not isinstance(other, Spec):
            return False
        return self.__dict__['spec'] == other.__dict__['spec']

    def __ne__(self, other):
        return not self.__eq__(other)

