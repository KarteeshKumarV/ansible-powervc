#!/usr/bin/python

"""
This module performs Consistency Group Create and Update operations
"""

import requests
import time


def get_headers(authtoken):
    return {
        "X-Auth-Token": authtoken,
        "Content-Type": "application/json",
        "Openstack-API-Version": "volume latest"
    }


def get_endpoint_url_by_service_name(mod, connectn, service_name, tenant_id):

    all_endpoints = connectn.identity.endpoints()
    services = connectn.identity.services()

    service_name_mapping = {service.id: service.type for service in services}

    service_id = next(
        (sid for sid, name in service_name_mapping.items() if name == service_name),
        None
    )

    if not service_id:
        mod.fail_json(
            msg=f"No service found with the name '{service_name}'",
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


def wait_for_group_available(module, url, headers, group_name):

    timeout_seconds = 120
    interval = 5
    elapsed = 0

    while elapsed < timeout_seconds:

        response = requests.get(
            url,
            headers=headers,
            verify=False,
            timeout=30
        )

        if not response.ok:
            module.fail_json(
                msg=f"Failed to verify consistency group: {response.json()}",
                changed=False,
            )

        group_status = response.json().get("group", {}).get("status")

        if group_status == "available":
            return

        if group_status == "error":
            module.fail_json(
                msg=f"Consistency group '{group_name}' entered error state.",
                changed=False,
            )

        time.sleep(interval)
        elapsed += interval

    module.fail_json(
        msg=f"Timeout waiting for consistency group '{group_name}' to become available.",
        changed=False,
    )

def create_consistency_group(module, createcg_url, authtoken, post_data, vol_data):

    headers = get_headers(authtoken)

    response = requests.post(
        createcg_url,
        headers=headers,
        json=post_data,
        verify=False,
        timeout=30
    )

    if not response.ok:
        module.fail_json(
            msg=f"Failed to create consistency group: {response.json()}",
            changed=False,
        )

    group = response.json().get("group", {})
    group_id = group.get("id")
    group_name = group.get("name")

    if not group_id:
        module.fail_json(
            msg="Group ID not returned from create API",
            changed=False,
        )

    group_url = f"{createcg_url}/{group_id}"

    wait_for_group_available(module, group_url, headers, group_name)

    if vol_data:
        put_response = requests.put(
            group_url,
            headers=headers,
            json={"group": vol_data},
            verify=False,
            timeout=30
        )

        if not put_response.ok:
            module.fail_json(
                msg=f"Failed to add volumes: {put_response.json()}",
                changed=False,
            )

        wait_for_group_available(module, group_url, headers, group_name)

    return f"Consistency Group '{group_name}' created successfully"


def createcg_ops(mod, connectn, authtoken, tenant_id,
                 name, group_type, volume_types,
                 description, vol_data):

    service_name = "volume"
    endpoint = get_endpoint_url_by_service_name(
        mod, connectn, service_name, tenant_id
    )

    group_body = {"name": name}

    if group_type:
        group_body["group_type"] = group_type

    if volume_types:
        group_body["volume_types"] = volume_types

    if description:
        group_body["description"] = description

    post_data = {"group": group_body}

    createcg_url = f"{endpoint}/groups"

    return create_consistency_group(
        mod,
        createcg_url,
        authtoken,
        post_data,
        vol_data
    )


def updatecg_ops(mod, connectn, authtoken, tenant_id,
                 group_id, update_payload, vol_data):

    service_name = "volume"
    endpoint = get_endpoint_url_by_service_name(
        mod, connectn, service_name, tenant_id
    )

    group_url = f"{endpoint}/groups/{group_id}"
    headers = get_headers(authtoken)

    get_resp = requests.get(
        group_url,
        headers=headers,
        verify=False,
        timeout=30
    )

    if not get_resp.ok:
        mod.fail_json(
            msg=f"Failed to fetch consistency group: {get_resp.json()}",
            changed=False
        )

    group_name = get_resp.json().get("group", {}).get("name")

    # Update name/description
    if update_payload:

        response = requests.put(
            group_url,
            headers=headers,
            json={"group": update_payload},
            verify=False,
            timeout=30
        )

        if not response.ok:
            mod.fail_json(
                msg=f"Failed to update group attributes: {response.json()}",
                changed=False
            )

        wait_for_group_available(mod, group_url, headers, group_name)

    # Add or Remove Volumes
    if vol_data:

        response = requests.put(
            group_url,
            headers=headers,
            json={"group": vol_data},
            verify=False,
            timeout=30
        )

        if not response.ok:
            mod.fail_json(
                msg=f"Failed to update volumes: {response.json()}",
                changed=False
            )

        wait_for_group_available(mod, group_url, headers, group_name)

    return f"Consistency Group '{group_name}' updated successfully"
