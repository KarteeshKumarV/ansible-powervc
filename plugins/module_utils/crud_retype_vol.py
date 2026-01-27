#!/usr/bin/python

"""
This module performs the Volume Retype operations.
"""

import requests
import json


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


def retype_vol(mod, authtoken, retype_url, post_data):
    headers_scg = get_headers(authtoken)
    responce = requests.post(retype_url, headers=headers_scg, json=post_data, verify=False)
    if responce.ok:
        return (
            "Volume Retype action is done",
        )
    else:
        mod.fail_json(
            msg=f"Volume Retype operation failed. {responce.json()}",
            changed=False,
        )


def retype_ops(mod, connectn, authtoken, tenant_id, vol_id, data):
    service_name = "volume"
    endpoint = get_endpoint_url_by_service_name(mod, connectn, service_name, tenant_id)
    retype_url = f"{endpoint}/volumes/{vol_id}/action"
    result = retype_vol(mod, authtoken, retype_url, data)
    return result
