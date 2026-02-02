#!/usr/bin/python

"""
This module helps in perfoming the registration and unregistration of an HMC host.
"""

import requests


def get_headers(authtoken):
    return {"X-Auth-Token": authtoken, "Content-Type": "application/json"}


def get_endpoint_url_by_service_name(connectn, service_name, tenant_id):
    """
    Get the endpoint url for that particular Service
    """
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
            return f"No endpoint found for service '{service_name}'"
    else:
        return f"No service found with the name '{service_name}'"


def delete_host(mod, authtoken, host_url):
    """
    Deletes the Host
    """
    headers_scg = get_headers(authtoken)
    responce = requests.delete(host_url, headers=headers_scg, verify=False)
    if responce.ok:
        return "Deleted the provided Host"
    else:
        mod.fail_json(
            msg=f"An unexpected error occurred: {responce.json()}", changed=False
        )


def post_host(module, authtoken, host_url, post_data):
    """
    Adds the HMC Host
    """
    headers_scg = get_headers(authtoken)
    responce = requests.post(host_url, headers=headers_scg, json=post_data, verify=False)
    if responce.ok:
        return (
            "Added the Host",
            responce.json(),
        )
    else:
        module.fail_json(
            msg=f"Failed in Adding the host: {responce.json()}",
            changed=False,
        )


def host_ops(mod, connectn, authtoken, tenant_id, state, host_id, data):
    """
    Performs the Host CRUD Operations based on the action input
    """
    service_name = "compute"
    endpoint = get_endpoint_url_by_service_name(connectn, service_name, tenant_id)
    if state == 'absent':
        host_url = endpoint + "/ibm-hmcs/" + host_id
        result = delete_host(mod, authtoken, host_url)
    elif state == 'present':
        host_url = endpoint + "/ibm-hmcs"
        result = post_host(mod, authtoken, host_url, data)
    return result
