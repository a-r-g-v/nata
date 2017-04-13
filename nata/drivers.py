from googleapiclient import discovery
from oauth2client.client import GoogleCredentials
import time

__cred = GoogleCredentials.get_application_default()
compute = discovery.build('compute', 'v1', credentials=__cred)


def wait_for_operation(compute, project, zone, operation):
    print('Waiting for operation to finish...')
    while True:
        if zone is not None:
            result = compute.zoneOperations().get(
                project=project, zone=zone, operation=operation).execute()
        else:
            result = compute.globalOperations().get(
                project=project, operation=operation).execute()

        if result['status'] == 'DONE':
            print("done.")
            if 'error' in result:
                raise Exception(result['error'])

            return result

        time.sleep(1)


def create_global_address(compute, name, data):
    body = {'name': name}
    return compute.globalAddresses().insert(
        project=data.project, body=body).execute()


def delete_global_address(compute, name, data):
    return compute.globalAddresses().delete(
        project=data.project, address=name).execute()


def list_global_address(compute, data):
    return compute.globalAddresses().list(project=data.project).execute()


def exist_global_address(compute, name, data):
    return exist_equals_name_in_item(compute, name, data, list_global_address)


def get_global_address(compute, name, data):
    result = list_global_address(compute, data)
    if 'items' not in result:
        raise KeyError("NotFound items in globalAddresses list")
    items = result["items"]
    for item in items:
        if name == item["name"]:
            return item["address"]
    else:
        raise Exception("NotFound %s in globalAddresse items" % name)


def update_global_forwarding_rule(compute, name, data, port=80):
    body = {
        'target':
        'https://www.googleapis.com/compute/v1/projects/{project}/global/targetHttpProxies/{name}'.
        format(project=data.project, name=data.name),
    }
    return compute.globalForwardingRules().setTarget(
        project=data.project, forwardingRule=name + str(port),
        body=body).execute()


def list_global_forwarding_rule(compute, data):
    return compute.globalForwardingRules().list(project=data.project).execute()


def delete_global_forwarding_rule(compute, name, data, port=80):
    return compute.globalForwardingRules().delete(
        project=data.project, forwardingRule=name + str(port)).execute()


def exist_global_forwarding_rule(compute, name, data, port=80):
    return exist_equals_name_in_item(compute, name + str(port), data,
                                     list_global_forwarding_rule)


def create_global_forwarding_rule(compute, name, data, ipaddr, port=80):
    resource = 'targetHttpProxies' if port == 80 else 'targetHttpsProxies'
    body = {
        'name':
        name + str(port),
        'portRange':
        port,
        'target':
        'https://www.googleapis.com/compute/v1/projects/{project}/global/{resource}/{name}'.
        format(project=data.project, name=data.name, resource=resource),
        'IPAddress':
        ipaddr
    }
    return compute.globalForwardingRules().insert(
        project=data.project, body=body).execute()


def list_target_https_proxy(compute, data):
    return compute.targetHttpsProxies().list(project=data.project).execute()


def delete_target_https_proxy(compute, name, data):
    return compute.targetHttpsProxies().delete(
        project=data.project, targetHttpsProxy=name).execute()


def exist_target_https_proxy(compute, name, data):
    return exist_equals_name_in_item(compute, name, data,
                                     list_target_https_proxy)


def create_target_https_proxy(compute, name, data):
    body = {
        'name': name,
        'urlMap': 'global/urlMaps/{name}'.format(name=data.name),
        'sslCertificates': data.sslCertificates
    }
    return compute.targetHttpsProxies().insert(
        project=data.project, body=body).execute()


def list_target_http_proxy(compute, data):
    return compute.targetHttpProxies().list(project=data.project).execute()


def delete_target_http_proxy(compute, name, data):
    return compute.targetHttpProxies().delete(
        project=data.project, targetHttpProxy=name).execute()


def exist_target_http_proxy(compute, name, data):
    return exist_equals_name_in_item(compute, name, data,
                                     list_target_http_proxy)


def create_target_http_proxy(compute, name, data):
    body = {
        'name': name,
        'urlMap': 'global/urlMaps/{name}'.format(name=data.name)
    }
    return compute.targetHttpProxies().insert(
        project=data.project, body=body).execute()


def list_url_map(compute, data):
    return compute.urlMaps().list(project=data.project).execute()


def exist_url_map(compute, name, data):
    return exist_equals_name_in_item(compute, name, data, list_url_map)


def delete_url_map(compute, name, data):
    return compute.urlMaps().delete(
        project=data.project, urlMap=name).execute()


def create_url_map(compute, name, data):
    body = {
        'name': name,
        'defaultService': 'global/backendServices/{name}'.format(
            name=data.name),
        'pathRules': []
    }
    return compute.urlMaps().insert(project=data.project, body=body).execute()


def list_http_health_check(compute, data):
    return compute.httpHealthChecks().list(project=data.project).execute()


def exist_http_health_check(compute, name, data):
    return exist_equals_name_in_item(compute, name, data,
                                     list_http_health_check)


def delete_http_health_check(compute, name, data):
    return compute.httpHealthChecks().delete(
        project=data.project, httpHealthCheck=name).execute()


def create_http_health_check(compute, name, data):
    body = {
        'name': name,
    }
    body.update(data.httpHealthCheck)
    return compute.httpHealthChecks().insert(
        project=data.project, body=body).execute()


def delete_backend_service(compute, name, data):
    return compute.backendServices().delete(
        project=data.project, backendService=name).execute()


def list_backend_service(compute, data):
    return compute.backendServices().list(project=data.project).execute()


def exist_backend_service(compute, name, data):
    return exist_equals_name_in_item(compute, name, data, list_backend_service)


def get_backend_service(compute, data, name):
    return compute.backendServices().get(
        project=data.project, backendService=name).execute()


def get_health_in_backend_service(compute, app_name, lb_name, data):
    instance_groups = "https://www.googleapi.com/compute/v1/projects/{project}/zones/{zone}/instanceGroups/{name}".format(
        project=data.project, zone=data.zone, name=app_name)
    body = {'group': instance_groups}
    return compute.backendServices().getHealth(
        project=data.project, backendService=lb_name, body=body).execute()


def update_backend_service(compute, data, app_name, lb_name):
    """
        data : application data
    """
    instance_groups = "https://www.googleapi.com/compute/v1/projects/{project}/zones/{zone}/instanceGroups/{name}".format(
        project=data.project, zone=data.zone, name=app_name)
    items = get_backend_service(compute, data, lb_name)
    if 'fingerprint' not in items:
        raise KeyError('Notfound fingerprint')

    body = {
        'backends': [{
            'group': instance_groups
        }],
    }
    items.update(body)

    return compute.backendServices().update(
        backendService=lb_name, project=data.project, body=items).execute()


def create_backend_service(compute, name, instance_groups_name, data):
    instance_groups = "https://www.googleapi.com/compute/v1/projects/{project}/zones/{zone}/instanceGroups/{name}".format(
        project=data.project, zone=data.zone, name=instance_groups_name)
    healthCheck = "projects/{project}/global/httpHealthChecks/{name}".format(
        project=data.project, name=data.name)

    body = {
        'name': name,
        'timeoutSec': data.LBtimeoutSec,
        'enableCDN': data.enableCDN,
        'backends': [{
            'group': instance_groups
        }],
        'healthChecks': [healthCheck]
    }
    return compute.backendServices().insert(
        project=data.project, body=body).execute()


def create_instance_template(compute, name, data):
    body = {"name": name, "properties": data.properties}

    return compute.instanceTemplates().insert(
        project=data.project, body=body).execute()


def delete_instance_template(compute, name, data):
    return compute.instanceTemplates().delete(
        project=data.project, instanceTemplate=name).execute()


def delete_instance(compute, name, data):
    return compute.instances().delete(
        project=data.project, zone=data.zone, instance=name).execute()


def list_managed_instance(compute, name, data):
    return compute.instanceGroupManagers().listManagedInstances(
        project=data.project, zone=data.zone,
        instanceGroupManager=name).execute()


def exist_instance_template(compute, name, data):
    return exist_equals_name_in_item(compute, name, data,
                                     list_instance_template)


def list_instance_template(compute, data):
    return compute.instanceTemplates().list(project=data.project).execute()


def list_instance_group_manager(compute, data):
    return compute.instanceGroupManagers().list(
        project=data.project, zone=data.zone).execute()


def exist_instance_group_manager(compute, name, data):
    return exist_equals_name_in_item(compute, name, data,
                                     list_instance_group_manager)


def delete_instance_group_manager(compute, name, data):
    return compute.instanceGroupManagers().delete(
        project=data.project, instanceGroupManager=name,
        zone=data.zone).execute()


def create_instance_group_manager(compute, name, data):
    instanceTemplateName = "projects/{project}/global/instanceTemplates/{name}".format(
        project=data.project, name=name)

    body = {
        'baseInstanceName': name,
        'name': name,
        'targetSize': 0,
        'instanceTemplate': instanceTemplateName
    }
    return compute.instanceGroupManagers().insert(
        project=data.project, zone=data.zone, body=body).execute()


def create_autoscaler(compute, name, data):
    target = 'https://www.googleapis.com/compute/v1/projects/{project}/zones/{zone}/instanceGroupManagers/{name}'.format(
        project=data.project, name=name, zone=data.zone)
    body = {
        'name': name,
        'target': target,
        'autoscalingPolicy': data.autoscalingPolicy
    }
    return compute.autoscalers().insert(
        project=data.project, zone=data.zone, body=body).execute()


def delete_autoscaler(compute, name, data):
    return compute.autoscalers().delete(
        project=data.project, autoscaler=name, zone=data.zone).execute()


def list_autoscaler(compute, data):
    return compute.autoscalers().list(
        project=data.project, zone=data.zone).execute()


def exist_autoscaler(compute, name, data):
    return exist_equals_name_in_item(compute, name, data, list_autoscaler)


def exist_equals_name_in_item(compute, name, data, list_func):
    result = list_func(compute, data)
    if 'items' not in result:
        return False

    items = result["items"]

    for item in items:
        if name == item["name"]:
            return True
    else:
        return False
