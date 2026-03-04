#!/usr/bin/python

"""
CRUD utilities for Volume Retype operation
"""

import requests


def get_headers(authtoken):
    return {
        "X-Auth-Token": authtoken,
        "Content-Type": "application/json"
    }


def get_endpoint_url_by_service_name(mod, connectn, service_name, tenant_id):
    all_endpoints = connectn.identity.endpoints()
    services = connectn.identity.services()
    service_map = {service.id: service.type for service in services}
    service_id = next(
        (sid for sid, name in service_map.items()
         if name == service_name),
        None
    )
    if not service_id:
        mod.fail_json(
            msg=f"No service found with name '{service_name}'",
            changed=False
        )
    endpoint = next(
        (ep for ep in all_endpoints if ep.service_id == service_id),
        None
    )
    if not endpoint:
        mod.fail_json(
            msg=f"No endpoint found for service '{service_name}'",
            changed=False
        )
    return endpoint.url.replace("%(tenant_id)s", tenant_id)


def retype_ops(mod, connectn, authtoken, tenant_id, vol_id, data):
    endpoint = get_endpoint_url_by_service_name(
        mod,
        connectn,
        "volume",
        tenant_id
    )
    retype_url = f"{endpoint}/volumes/{vol_id}/action"
    response = requests.post(
        retype_url,
        headers=get_headers(authtoken),
        json=data,
        verify=False,
        timeout=30
    )
    if response.status_code not in [200, 202]:
        mod.fail_json(
            msg="Volume retype operation failed",
            response=response.text,
            changed=False
        )
    return {
        "msg": f"Volume '{vol_id}' retype operation triggered successfully",
    }
