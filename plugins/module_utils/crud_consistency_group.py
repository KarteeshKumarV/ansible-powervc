#!/usr/bin/python

"""
This module performs the Consistency Group create operations
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


def create_consistency_group(module, createcg_url, authtoken, post_data, vol_data):
    """
    Performs Create Consistency Group Operations
    """
    headers_cg = {"X-Auth-Token": authtoken, "Content-Type": "application/json", "Openstack-API-Version": "volume latest"}
    response = requests.post(createcg_url, headers=headers_cg, json=post_data, verify=False, timeout=30)
    if not response.ok:
        module.fail_json(
            msg=f"Create failed: {response.text}",
            changed=False
        )
    group_id = response.json()["group"]["id"]
    group_name = response.json()["group"]["name"]
    get_url = f"{createcg_url}/{group_id}"
    verify_response = requests.get(get_url, headers=headers_cg, verify=False, timeout=30)
    if not verify_response.ok:
        module.fail_json(
            msg=f"Group '{group_name}' not found.",
            changed=False,
        )
    verify_data = verify_response.json().get("group", {})
    if verify_data.get("name") != group_name:
        module.fail_json(
            msg="Create Consistency Group failed - Mismatch in group name during verification.",
            changed=False,
        )
    if vol_data:
        add_vol_url = f"{createcg_url}/{group_id}"
        put_response = requests.put(add_vol_url, headers=headers_cg, json=vol_data, verify=False, timeout=30)
        if put_response.ok:
            return (
                f"Consistency Group '{group_name}' created and volumes added successfully",
            )
        else:
            module.fail_json(
                msg=f"{response.json()}",
                changed=False,
            )
    return f"Consistency Group '{group_name}' created successfully"

def createcg_ops(mod, connectn, authtoken, tenant_id, name, group_type, volume_types, description, vol_data):
    service_name = "volume"
    endpoint = get_endpoint_url_by_service_name(mod, connectn, service_name, tenant_id)
    group_body = {"name": name}

    if group_type:
        group_body["group_type"] = group_type

    if volume_types:
        group_body["volume_types"] = volume_types

    if description:
        group_body["description"] = description

    post_data = {"group": group_body}

    createcg_url = f"{endpoint}/groups"
    result = create_consistency_group(mod, createcg_url, authtoken, post_data, vol_data)
    return result
