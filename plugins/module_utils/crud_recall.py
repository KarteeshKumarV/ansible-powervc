#!/usr/bin/python

"""
This module performs the Recall operations on the Host
"""

import requests


def get_headers(authtoken):
    return {"X-Auth-Token": authtoken, "Content-Type": "application/json"}


def get_endpoint_url_by_service_name(mod, connectn, service_name, tenant_id):
    all_endpoints = connectn.identity.endpoints()
    services = connectn.identity.services()
    service_name_mapping = {service.id: service.type for service in services}
    service_id = next(
        (id for id, name in service_name_mapping.items() if name == service_name), None
    )
    if service_id:
        endpoint = next(
            (ep for ep in all_endpoints if ep.service_id == service_id), None
        )
        if endpoint:
            return endpoint.url.replace("%(tenant_id)s", tenant_id)
        else:
            mod.fail_json(msg=f"No endpoint found for service '{service_name}'", changed=False)
    else:
        mod.fail_json(msg=f"No service found with the name '{service_name}'", changed=False)


def put_recall(mod, endpoint, url, authtoken, put_data):
    headers_scg = {"X-Auth-Token": authtoken, "Content-Type": "application/json"}
    responce = requests.put(url, headers=headers_scg, verify=False)
    if responce.ok:
        return f"Recall Host Operation Done"
    else:
        mod.fail_json(
            msg=f"An unexpected error occurred:{responce.json()}", changed=False
        )


def recall_ops(mod, connectn, authtoken, tenant_id, host_display_name_value):
    service_name = "compute"
    headers_scg = {"X-Auth-Token": authtoken, "Content-Type": "application/json"}
    endpoint = get_endpoint_url_by_service_name(mod, connectn, service_name, tenant_id)
    url = f"{endpoint}/os-hosts/{host_display_name_value}/recall-vm"
    data = {"recall_vm": "true"}
    result = put_recall(mod, endpoint, url, authtoken, data)
    return result
