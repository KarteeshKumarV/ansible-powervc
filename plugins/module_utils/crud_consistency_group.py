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
    headers_scg = {"X-Auth-Token": authtoken, "Content-Type": "application/json", "Openstack-API-Version": "volume latest"}
    responce = requests.post(createcg_url, headers=headers_scg, json=post_data, verify=False)
    if responce.ok:
        group_id = responce.json()["group"]["id"]
        group_name = responce.json()["group"]["name"]
        add_vol_url = f"{createcg_url}/{group_id}"
        responce = requests.put(add_vol_url, headers=headers_scg, json=vol_data, verify=False)
        return (
            f"Consistency Group '{group_name}' has been created",
        )
    else:
        module.fail_json(
            msg=f"{responce.json()}",
            changed=False,
        )


def createcg_ops(mod, connectn, authtoken, tenant_id, name, vol_data, group_type, storage_provider, description):
    service_name = "volume"
    endpoint = get_endpoint_url_by_service_name(mod, connectn, service_name, tenant_id)
    post_data = {"group": {"name": name, "group_type": group_type , "volume_types": [storage_provider], "description": description}}
    createcg_url = f"{endpoint}/groups"
    result = create_consistency_group(mod, createcg_url, authtoken, post_data, vol_data)
    return result

