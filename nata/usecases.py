from prettytable import PrettyTable
from .mappers import AppMapper, ServiceMapper, LbMapper
from .domains import Spec, Service, App, Lb
from .resources import LbResource, AppResource
from .drivers import *
import sys
import csv


def app_factory(new_app_name, spec, service):
    new_app = App(new_app_name, spec, service)

    new_app_resource = AppResource(new_app)
    if new_app_resource.exist():
        raise Exception('Already exists AppResource : %s', new_app.name)

    try:
        new_app_resource.create()
        AppMapper.insert(new_app)
    except Exception:
        raise

    return new_app


def lb_factory(new_lb_name, spec, target_app, service):
    new_lb = Lb(new_lb_name, spec, target_app, service)

    target_app_resource = AppResource(target_app)
    if not target_app_resource.exist():
        raise Exception('target_app is not exists : %s',
                        target_app_resource.name)

    new_lb_resource = LbResource(new_lb, target_app)
    if new_lb_resource.exist():
        raise Exception('Already exists AppResource : %s', new_lb.name)

    try:
        new_lb_resource.create()
        LbMapper.insert(new_lb)
    except Exception:
        raise

    return new_lb


class ServiceUseCase(object):

    @classmethod
    def rolling(cls, name):
        service = ServiceMapper.get(name)
        app_resource = AppResource(service.get_primary_app())
        app_resource.rolling()

    @classmethod
    def create(cls, spec):
        new_service = Service(spec.name, spec)
        ServiceMapper.insert(new_service)

        new_app_name = App.generate_name(spec.name)
        new_app = app_factory(new_app_name, spec, new_service)

        new_lb = lb_factory(spec.name, spec, new_app, new_service)

        new_service.set_app(new_app)
        new_service.set_lb(new_lb)
        ServiceMapper.update(new_service)

    @classmethod
    def delete(cls, service_name):
        service = ServiceMapper.get(service_name)
        lb_resource = LbResource(service.lb, service.get_primary_app())
        lb_resource.delete()

        for app in service.apps:
            app_resource = AppResource(app)
            app_resource.delete()
        ServiceMapper.delete(service)

    @classmethod
    def list(cls):
        services = ServiceMapper.list()
        fileds = ['name', 'primary_app_name', 'address', 'created_date']
        table = PrettyTable(fileds)

        for service in services:
            address = "" if service.lb.address is None else service.lb.address
            table.add_row([
                service.name, service.get_primary_app().name, address,
                service.created_date
            ])

        print(table)
        return services

    @classmethod
    def switch(cls, service_name, app_name):
        service = ServiceMapper.get(service_name)
        target_app = AppMapper.get(app_name)

        if target_app.primary:
            raise Exception('The application is primary.')

        if target_app.service != service:
            raise Exception(
                'The service that %s application belong is diffrent from %s.' %
                target_app.name, app_name)

        lb = LbResource(service.lb, service.get_primary_app())
        assert lb.exist()

        lb.switch(target_app)

        service.get_primary_app().primary = False
        service.lb.app = target_app
        target_app.primary = True

        ServiceMapper.update(service)


class AppUseCase(object):

    @classmethod
    def create(cls, spec):
        service = ServiceMapper.get(spec.name)
        if service is None:
            raise Exception('%s service is not exists.' % spec.name)

        new_app_name = App.generate_name(spec.name)
        new_app = app_factory(new_app_name, spec, service)
        service.set_app(new_app)

    @classmethod
    def delete(cls, app_name):
        app = AppMapper.get(app_name)
        if app is None:
            raise Exception('%s app is not exists.' % app_name)

        if app.primary:
            raise Exception('Primary Application cannot delete')

        app_resource = AppResource(app)
        app_resource.delete()

        AppMapper.delete(app)

    @classmethod
    def list(cls):
        apps = AppMapper.list()
        fields = ['name', 'service', 'primary', 'image', 'created_date']
        table = PrettyTable(fields)

        for app in apps:
            is_primary = 'Yes' if app.primary else 'No'
            table.add_row([
                app.name, app.service.name, is_primary, None, app.created_date
            ])

        print(table)
        return apps


class DebugUseCase(object):
    @classmethod
    def do(cls):
        data = {'project': 'nata-jp', 'zone': 'asia-northeast1-a'}
        data = Spec(spec=data)
        # for LB
        result = list_global_address(compute, data)

        if 'items' in result:
            for item in result['items']:
                cls.delete_service_and_app(item['name'])

        # for App
        result = list_instance_template(compute, data)

        if 'items' in result:
            for item in result['items']:
                cls.delete_service_and_app(item['name'])

    @classmethod
    def delete_service_and_app(cls, name):
        data = {
            'project': 'nata-jp',
            'name': name,
            'zone': 'asia-northeast1-a'
        }
        data = Spec(spec=data)
        if exist_global_forwarding_rule(compute, name, data):
            op = delete_global_forwarding_rule(compute, name, data)
            wait_for_operation(compute, data.project, None, op["name"])

        if exist_global_address(compute, name, data):
            op = delete_global_address(compute, name, data)
            wait_for_operation(compute, data.project, None, op["name"])

        if exist_target_http_proxy(compute, name, data):
            op = delete_target_http_proxy(compute, name, data)
            wait_for_operation(compute, data.project, None, op["name"])

        if exist_url_map(compute, name, data):
            op = delete_url_map(compute, name, data)
            wait_for_operation(compute, data.project, None, op["name"])

        if exist_backend_service(compute, name, data):
            op = delete_backend_service(compute, name, data)
            wait_for_operation(compute, data.project, None, op["name"])

        if exist_http_health_check(compute, name, data):
            op = delete_http_health_check(compute, name, data)
            wait_for_operation(compute, data.project, None, op["name"])

        if exist_autoscaler(compute, name, data):
            op = delete_autoscaler(compute, name, data)
            wait_for_operation(compute, data.project, data.zone, op["name"])

        if exist_instance_group_manager(compute, name, data):
            op = delete_instance_group_manager(compute, data.name, data)
            wait_for_operation(compute, data.project, data.zone, op["name"])

        if exist_instance_template(compute, name, data):
            op = delete_instance_template(compute, data.name, data)
            wait_for_operation(compute, data.project, None, op["name"])
