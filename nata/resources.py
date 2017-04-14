from .drivers import *
from . import logger
import json
import time


class LbResource(object):
    def __init__(self, lb, app, enable_https=False):
        self.lb = lb
        self.name = lb.name
        self.spec = self.lb.spec
        self.app = app
        self.enable_https = enable_https

    def remote_exist_resources(self):
        result = []

        if exist_global_forwarding_rule(
                compute, self.name, self.spec, port=80):
            result.append('global_forwarding_rule_http')

        if exist_global_forwarding_rule(
                compute, self.name, self.spec, port=443):
            result.append('global_forwarding_rule_https')

        if exist_global_address(compute, self.name, self.spec):
            result.append('global_address')

        if exist_target_http_proxy(compute, self.name, self.spec):
            result.append('target_http_proxy')

        if exist_target_https_proxy(compute, self.name, self.spec):
            result.append('target_https_proxy')

        if exist_url_map(compute, self.name, self.spec):
            result.append('url_map')

        if exist_backend_service(compute, self.name, self.spec):
            result.append('backend_service')

        if exist_http_health_check(compute, self.name, self.spec):
            result.append('http_health_check')

        return result

    def exist(self):
        return len(self.remote_exist_resources()) >= 6

    def create(self):
        op = create_http_health_check(compute, self.name, self.spec)
        wait_for_operation(compute, self.spec.project, None, op["name"])

        op = create_backend_service(compute, self.name, self.app.name,
                                    self.spec)
        wait_for_operation(compute, self.spec.project, None, op["name"])

        op = create_url_map(compute, self.name, self.spec)
        wait_for_operation(compute, self.spec.project, None, op["name"])

        op = create_target_http_proxy(compute, self.name, self.spec)
        wait_for_operation(compute, self.spec.project, None, op["name"])

        if self.enable_https:
            op = create_target_https_proxy(compute, self.name, self.spec)
            wait_for_operation(compute, self.spec.project, None, op["name"])

        op = create_global_address(compute, self.name, self.spec)
        wait_for_operation(compute, self.spec.project, None, op["name"])

        ipaddr = get_global_address(compute, self.name, self.spec)
        self.lb.address = ipaddr

        op = create_global_forwarding_rule(
            compute, self.name, self.spec, ipaddr, port=80)
        wait_for_operation(compute, self.spec.project, None, op["name"])

        if self.enable_https:
            op = create_global_forwarding_rule(
                compute, self.name, self.spec, ipaddr, port=443)
            wait_for_operation(compute, self.spec.project, None, op["name"])

    def delete(self):
        if exist_global_forwarding_rule(
                compute, self.name, self.spec, port=80):
            op = delete_global_forwarding_rule(
                compute, self.name, self.spec, port=80)
            wait_for_operation(compute, self.spec.project, None, op["name"])

        if self.enable_https and exist_global_forwarding_rule(
                compute, self.name, self.spec, port=443):
            op = delete_global_forwarding_rule(
                compute, self.name, self.spec, port=443)
            wait_for_operation(compute, self.spec.project, None, op["name"])

        if exist_global_address(compute, self.name, self.spec):
            op = delete_global_address(compute, self.name, self.spec)
            wait_for_operation(compute, self.spec.project, None, op["name"])

        if exist_target_http_proxy(compute, self.name, self.spec):
            op = delete_target_http_proxy(compute, self.name, self.spec)
            wait_for_operation(compute, self.spec.project, None, op["name"])

        if self.enable_https and exist_target_https_proxy(
                compute, self.name, self.spec):
            op = delete_target_https_proxy(compute, self.name, self.spec)
            wait_for_operation(compute, self.spec.project, None, op["name"])

        if exist_url_map(compute, self.name, self.spec):
            op = delete_url_map(compute, self.name, self.spec)
            wait_for_operation(compute, self.spec.project, None, op["name"])

        if exist_backend_service(compute, self.name, self.spec):
            op = delete_backend_service(compute, self.name, self.spec)
            wait_for_operation(compute, self.spec.project, None, op["name"])

        if exist_http_health_check(compute, self.name, self.spec):
            op = delete_http_health_check(compute, self.name, self.spec)
            wait_for_operation(compute, self.spec.project, None, op["name"])

    def switch(self, app):
        op = update_backend_service(compute, app.spec, app.name, self.name)
        wait_for_operation(compute, app.spec.project, None, op["name"])


class AppResource(object):
    def __init__(self, app):
        self.app = app
        self.name = app.name
        self.spec = self.app.spec

    def get_health_in_backend_service(self, lb):
        for _ in range(5):
            health_status = get_health_in_backend_service(compute, self.name,
                                                      lb.name, self.spec)
            if 'healthStatus' in health_status:
                return health_status
            time.sleep(60)

    def count_stable_instances(self, lb):
        health_status = self.get_health_in_backend_service(lb)
        cnt = 0
        for health in health_status['healthStatus']:
            if health['healthState'] == 'HEALTHY':
                cnt += 1
        return cnt

    def wait_for_stable(self, lb, desire_stable_count):
        now_count = self.count_stable_instances(lb)
        while now_count != desire_stable_count:
            logger.debug('wait some maneged instances until stable... now: %d, desire: %d' % (now_count, desire_stable_count,))
            print('wait instances until stable... now : %d, desire %d' % (now_count, desire_stable_count,))
            now_count = self.count_stable_instances(lb)
            time.sleep(20)

    def rolling(self, lb):

        result = self.get_health_in_backend_service(lb)
        desire_stable_count = self.count_stable_instances(lb)

        if 'healthStatus' not in result:
            raise Exception

        for instance in result['healthStatus']:
            self.wait_for_stable(lb, desire_stable_count)
            instance_name = instance['instance'].split('/')[-1]
            op = delete_instance(compute, instance_name, self.spec)
            wait_for_operation(compute, self.spec.project, self.spec.zone,
                               op["name"])

    def remote_exist_resources(self):
        result = []

        if exist_instance_template(compute, self.name, self.spec):
            result.append('instance_template')

        if exist_instance_group_manager(compute, self.name, self.spec):
            result.append('group_manager')

        if exist_autoscaler(compute, self.name, self.spec):
            result.append('autoscaler')

        return result

    def exist(self):
        return len(self.remote_exist_resources()) >= 3

    def create(self):
        exists_resources = self.remote_exist_resources()
        if len(exists_resources) != 0:
            raise Exception('Already resources exists : {resources}'.format(
                resources=", ".join(exists_resources)))

        op = create_instance_template(compute, self.name, self.spec)
        wait_for_operation(compute, self.spec.project, None, op["name"])
        logger.debug('created instance_template: %s' % self.name)

        op = create_instance_group_manager(compute, self.name, self.spec)
        wait_for_operation(compute, self.spec.project, self.spec.zone,
                           op["name"])
        logger.debug('created instance_group_maneger: %s' % self.name)

        op = create_autoscaler(compute, self.name, self.spec)
        wait_for_operation(compute, self.spec.project, self.spec.zone,
                           op["name"])
        logger.debug('created autoscaler: %s' % self.name)

    def delete(self):
        if not self.exist():
            raise Exception('NotFound App Resorces')

        if exist_autoscaler(compute, self.name, self.spec):
            op = delete_autoscaler(compute, self.name, self.spec)
            wait_for_operation(compute, self.spec.project, self.spec.zone,
                               op["name"])
            logger.debug('deleted autoscaler: %s' % self.name)

        if exist_instance_group_manager(compute, self.name, self.spec):
            op = delete_instance_group_manager(compute, self.name, self.spec)
            wait_for_operation(compute, self.spec.project, self.spec.zone,
                               op["name"])
            logger.debug('deleted instance_group_maneger: %s', self.name)

        if exist_instance_template(compute, self.name, self.spec):
            op = delete_instance_template(compute, self.name, self.spec)
            wait_for_operation(compute, self.spec.project, None, op["name"])
            logger.debug('deleted instance_template: %s', self.name)
