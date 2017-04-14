from datetime import datetime
from human_dates import time_ago_in_words

import uuid
import yaml as yam
import json

class HumanDate():
    @classmethod
    def time_ago_in_words(cls, time):
        # type: (datetime) -> str
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
                return "a minute ago"
            if second_diff < 3600:
                return str(second_diff / 60) + " minutes ago"
            if second_diff < 7200:
                return "an hour ago"
            if second_diff < 86400:
                return str(second_diff / 3600) + " hours ago"
        if day_diff == 1:
            return "Yesterday"
        if day_diff < 7:
            return str(day_diff) + " days ago"
        if day_diff < 31:
            return str(day_diff / 7) + " weeks ago"
        if day_diff < 365:
            return str(day_diff / 30) + " months ago"
        return str(day_diff / 365) + " years ago"

    @property
    def created_date(self):
        # type: () -> str
        return self.time_ago_in_words(self._created_date)


class Service(object, HumanDate):
    def __init__(self, name, spec):
        # type: (str, Spec) -> None
        self.name = name
        self.spec = spec
        self.lb = None
        self.apps = []

    def set_app(self, app):
        # type: (App) -> None
        self.apps.append(app)

    def set_lb(self, lb):
        # type: (Lb) -> None
        self.lb = lb

    def get_primary_app(self):
        # type: () -> App
        for app in self.apps:
            if app.primary:
                return app

        raise Exception('primary application is not exist.')

    def __eq__(self, other):
        # type: (Service) -> bool
        if other is None or not isinstance(other, Service):
            return False
        return self.name == other.name

    def __ne__(self, other):
        # type: (Service) -> bool
        return not self.__eq__(other)


class App(object, HumanDate):
    def __init__(self, name, spec, service):
        # type: (str, Spec, Service) -> None
        self.name = name
        self.spec = spec
        self.primary = False  # read only attr
        self.service = service

    @staticmethod
    def generate_name(name):
        # type: (str) -> str
        return name + uuid.uuid4().hex[0:6]

    def __eq__(self, other):
        # type: (App) -> bool
        if other is None or not isinstance(other, App):
            return False
        return self.name == other.name

    def __ne__(self, other):
        # type: (App) -> bool
        return not self.__eq__(other)


class Lb(object):
    def __init__(self, name, spec, app, service):
        # type: (str, Spec, App, Service) -> None
        self.name = name
        self.spec = spec
        self.app = app
        self.service = service
        self.address = None

    def __eq__(self, other):
        # type: (Lb) -> bool
        if other is None or not isinstance(other, Lb):
            return False
        return self.name == other.name

    def __ne__(self, other):
        # type: (Lb) -> bool
        return not self.__eq__(other)


class Spec(object):
    def __init__(self, spec=None, filename=None, yaml=None):
        # type: (Union[None, Dict[str, str]], Union[None, str], Union[None, yaml]) -> None
        
        if filename is not None:
            self.spec = yam.load(file(filename))
        if yaml is not None:
            self.spec = yam.load(yaml)
        if spec is not None:
            self.spec = spec

    def __getattr__(self, key):
        # type: (str, str) -> Union[None, str]
        if key not in self.spec:
            raise AttributeError
        return self.spec[key]

    def __setattr__(self, key, value):
        # type: (str, str) -> None
        if key == 'spec':
            self.__dict__['spec'] = value
        else:
            dic = self.__dict__['spec']
            dic[key] = value

    def __delattr__(self, key):
        # type: (str) -> None
        del self.spec[key]

    def to_json(self):
        # type: () -> str
        return json.dumps(self.spec)

    def __eq__(self, other):
        # type: (Spec) -> bool
        if other is None or not isinstance(other, Spec):
            return False
        return self.__dict__['spec'] == other.__dict__['spec']

    def __ne__(self, other):
        # type: (Spec) -> bool
        return not self.__eq__(other)

    @property
    def image_name(self):
        # type: () -> str
        for disk in self.spec['properties'][0]['disks']:
            if disk['boot'] is False:
                continue
            return disk['initializeParams'][0]['sourceImage']

