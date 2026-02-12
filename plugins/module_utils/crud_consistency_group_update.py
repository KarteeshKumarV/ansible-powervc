#!/usr/bin/python

"""
This module performs the Consistency Group update operations
"""

import requests


def get_endpoint_url_by_service_name(mod, connectn, service_name, tenant_id):
    all_endpoints = connectn.identity.endpoints()
    services = connectn.identity.services()

    service_name_mapping = {service.id: service.type for service in services}

    service_id = next(
        (sid for sid, name in service_name_mapping.items() if name == service_name),
        None,
    )

    if not service_id:
        mod.fail_json(
            msg=f"No service found with the name '{service_name}'",
            changed=False,
        )

    endpoint = next(
        (ep for ep in all_endpoints if ep.service_id == service_id),
        None,
    )

    if not endpoint:
        mod.fail_json(
            msg=f"No endpoint found for service '{service_name}'",
            changed=False,
        )

    return endpoint.url.replace("%(tenant_id)s", tenant_id)


def update_consistency_group(module, updatecg_url, authtoken, post_data):
    """
    Performs Consistency Group Update Operation
    """

    headers = {"X-Auth-Token": authtoken, "Content-Type": "application/json", "Openstack-API-Version": "volume latest"}

    response = requests.put(updatecg_url, headers=headers, json=post_data, verify=False)
    if response.ok:
        return (
                f"Consistency Group has been updated : {post_data}",
        )
    else:
        module.fail_json(
            msg=f"{response.json()}",
            changed=False,
        )


def updatecg_ops(mod, connectn, authtoken, tenant_id,
                 group_id, name=None, description=None, volume_data=None):

    service_name = "volume"

    endpoint = get_endpoint_url_by_service_name(
        mod, connectn, service_name, tenant_id
    )

    group_data = {}

    if name is not None:
        group_data["name"] = name

    if description is not None:
        group_data["description"] = description

    if volume_data:
        group_data.update(volume_data)

    if not group_data:
        mod.fail_json(
            msg="Nothing to update. Provide name, description, or volume.",
            changed=False,
        )

    post_data = {"group": group_data}

    updatecg_url = f"{endpoint}/groups/{group_id}"

    result = update_consistency_group(mod, updatecg_url, authtoken, post_data)

    return result

