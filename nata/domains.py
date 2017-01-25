
class HumanDate():

    def time_ago_in_words(cls, time):
        from datetime import datetime
        now = datetime.now()
        diff = now - time
        
        second_diff = diff.seconds
        day_diff = diff.days
        if day_diff < 0:
            return ''

        if day_diff == 0:
            if second_diff < 10:
                return "just now"
            if second_diff < 60:
                return str(second_diff) + " seconds ago"
            if second_diff < 120:
                return  "a minute ago"
            if second_diff < 3600:
                return str( second_diff / 60 ) + " minutes ago"
            if second_diff < 7200:
                return "an hour ago"
            if second_diff < 86400:
                return str( second_diff / 3600 ) + " hours ago"
        if day_diff == 1:
            return "Yesterday"
        if day_diff < 7:
            return str(day_diff) + " days ago"
        if day_diff < 31:
            return str(day_diff/7) + " weeks ago"
        if day_diff < 365:
            return str(day_diff/30) + " months ago"
        return str(day_diff/365) + " years ago"

    @property
    def created_date(self):
        from human_dates import time_ago_in_words
        return self.time_ago_in_words(self._created_date)

class Service(object, HumanDate):

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


class App(object, HumanDate):

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

