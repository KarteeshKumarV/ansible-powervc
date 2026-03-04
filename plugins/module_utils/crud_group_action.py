#!/usr/bin/python

"""
CRUD utilities for Consistency Group Action APIs
"""

import requests


def get_headers(authtoken):
    return {
        "X-Auth-Token": authtoken,
        "Content-Type": "application/json",
        "Openstack-API-Version": "volume latest"
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


def group_action(
    module,
    connectn,
    authtoken,
    tenant_id,
    group_id,
    action,
    secondary=None,
    primary=None,
    access=None
):
    endpoint = get_endpoint_url_by_service_name(
        module,
        connectn,
        "volume",
        tenant_id
    )
    headers = get_headers(authtoken)
    url = f"{endpoint}/groups/{group_id}/action"
    if action == "show":
        body = {"group-show": {"secondary": secondary}}
        changed = False
    elif action == "relationship":
        body = {"group-relationships": {"secondary": secondary}}
        changed = False
    elif action == "start":
        body = {"group-start": {"primary": primary}}
        changed = True
    elif action == "stop":
        body = {"group-stop": {"access": access}}
        changed = True
    else:
        module.fail_json(
            msg=f"Unsupported action '{action}'",
            changed=False
        )
    response = requests.post(
        url,
        headers=headers,
        json=body,
        verify=False,
        timeout=30
    )
    if response.status_code not in [200, 202]:
        module.fail_json(
            msg=f"Failed to execute action '{action}'",
            status_code=response.status_code,
            response=response.text,
            changed=False
        )
    if action in ["start", "stop"]:
        result = {
            "msg": f"Consistency group '{group_id}' {action} operation triggered successfully",
        }
    else:
        result = response.json()
    return result, changed
