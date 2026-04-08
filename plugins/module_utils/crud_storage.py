#!/usr/bin/python

import requests


def get_headers(authtoken):
    return {
        "X-Auth-Token": authtoken,
        "Content-Type": "application/json",
        "Openstack-API-Version": "volume latest",
    }


def get_endpoint_url_by_service_name(mod, connectn, service_name, tenant_id):
    all_endpoints = connectn.identity.endpoints()
    services = connectn.identity.services()
    service_map = {service.id: service.type for service in services}
    service_id = next(
        (sid for sid, name in service_map.items() if name == service_name), None
    )
    if not service_id:
        mod.fail_json(msg=f"No service found: {service_name}")
    endpoint = next(
        (ep for ep in all_endpoints if ep.service_id == service_id), None
    )
    if not endpoint:
        mod.fail_json(msg=f"No endpoint found for {service_name}")
    return endpoint.url.replace("%(tenant_id)s", tenant_id)


def storage_ops(module, endpoint, authtoken, tenant_id, verify, state, storage_id=None, body=None):
    headers = get_headers(authtoken)
    if state == "absent":
        if not storage_id:
            module.fail_json(msg="host name from storage specific metadata is required")
        url = f"{endpoint}/os-hosts/{storage_id}"
        response = requests.delete(url, headers=headers, verify=verify)
        if response.status_code == 204:
            return dict(changed=True, msg="Storage remove operation initiated successfully")
        module.fail_json(
            msg="Failed to remove the storage",
            status_code=response.status_code,
            response=response.text,
        )
    if state == "present" and body and not storage_id:
        url = f"{endpoint}/os-hosts"
        response = requests.post(
            url,
            headers=headers,
            json=body,
            verify=verify,
        )
        if response.status_code in [200, 202]:
            return dict(
                changed=True,
                msg="Storage registered successfully",
                result=response.json(),
            )
        module.fail_json(
            msg="Failed to add storage",
            status_code=response.status_code,
            response=response.text,
        )
    if state == "present" and storage_id and body:
        url = f"{endpoint}/os-hosts/{storage_id}"
        response = requests.put(url, headers=headers, json=body, verify=verify)
        if response.status_code == 200:
            return dict(changed=True, msg="Updated", result=response.json())
        module.fail_json(
            msg="Failed to update storage",
            status_code=response.status_code,
            response=response.text,
        )
    if state == "present" and storage_id:
        url = f"{endpoint}/os-hosts/{storage_id}"
        response = requests.get(url, headers=headers, verify=verify)
        if response.status_code != 200:
            module.fail_json(
                msg=f"Failed to fetch stoarge details",
                status_code=response.status_code,
                response=response.text,
            )
        return dict(changed=False, result=response.json())
    if state == "present":
        url = f"{endpoint}/os-hosts/detail"
        response = requests.get(url, headers=headers, verify=verify)
        if response.status_code != 200:
            module.fail_json(
                msg="Failed to fetch stoarge details",
                status_code=response.status_code,
                response=response.text,
            )
        return dict(changed=False, result=response.json())
