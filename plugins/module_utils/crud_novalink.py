#!/usr/bin/python

"""
This module helps in perfoming the registration and unregistration of the Novalink host.
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


def delete_host(mod, authtoken, host_url, host_id):
    """
    Removes the Host
    """
    headers_scg = get_headers(authtoken)
    responce = requests.delete(host_url, headers=headers_scg, verify=False)
    if responce.ok:
        return dict(
            changed=True,
            msg=f"Removed the Novalink Host: {host_id}"
        )
    else:
        mod.fail_json(
            msg=f"An unexpected error occurred: {responce.json()}", changed=False
        )


def post_host(module, authtoken, host_url, post_data):
    headers_scg = get_headers(authtoken)
    response = requests.post(host_url, headers=headers_scg, json=post_data, verify=False)
    if response.ok:
        return dict(
            changed=True,
            msg="Added the Host",
            result=response.json()
        )
    else:
        module.fail_json(
            msg=f"Failed in Adding the host: {response.json()}",
            changed=False,
        )


def put_host(module, authtoken, host_url, body):
    headers_scg = get_headers(authtoken)
    response = requests.put(
        host_url,
        headers=headers_scg,
        json=body,
        verify=False
    )

    if response.ok:
        resp = response.json()
        if "private_key_data" in resp.get("registration", {}):
            resp["registration"]["private_key_data"] = "VALUE_SPECIFIED_IN_NO_LOG_PARAMETER"
        return dict(
            changed=True,
            msg="Updated the Host",
            result=resp
        )
    else:
        module.fail_json(
            msg=f"Failed in updating host: {response.json()}",
            changed=False,
        )


def host_ops(mod, connectn, authtoken, tenant_id, state, host_id, data):
    """
    Performs the Host CRUD Operations based on the action input
    """
    service_name = "compute"
    endpoint = get_endpoint_url_by_service_name(connectn, service_name, tenant_id)
    if state == 'absent':
        if data == "uninstall_novalink":
            host_url = f"{endpoint}/os-hosts/{host_id}/uninstall"
        else:
            host_url = f"{endpoint}/os-hosts/{host_id}"
        result = delete_host(mod, authtoken, host_url, host_id)
    elif state == 'present' and host_id:
        host_url = (
            f"{endpoint}/os-hosts/"
            f"{host_id}/update-registration"
        )
        result = put_host(
            mod,
            authtoken,
            host_url,
            data
        )
    elif state == 'present':
        host_url = endpoint + "/os-hosts"
        result = post_host(mod, authtoken, host_url, data)
    return result
