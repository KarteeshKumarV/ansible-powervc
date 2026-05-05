#!/usr/bin/python

"""
CRUD utility for PowerVC VM migration operations.

Supports:
- Live migration
- Cold migration
- Cross host-group migration using ignore_az
"""

import requests


def get_headers(auth_token):
    return {
        "X-Auth-Token": auth_token,
        "Content-Type": "application/json"
    }


def get_endpoint_url_by_service_name(
    mod,
    connection,
    service_name,
    tenant_id
):
    all_endpoints = connection.identity.endpoints()
    services = connection.identity.services()
    service_map = {
        service.id: service.type
        for service in services
    }
    service_id = next(
        (
            sid for sid, name in service_map.items()
            if name == service_name
        ),
        None
    )
    if not service_id:
        mod.fail_json(
            msg=f"No service found with name '{service_name}'",
            changed=False
        )
    endpoint = next(
        (
            ep for ep in all_endpoints
            if ep.service_id == service_id
        ),
        None
    )
    if not endpoint:
        mod.fail_json(
            msg=f"No endpoint found for service '{service_name}'",
            changed=False
        )
    return endpoint.url.replace(
        "%(tenant_id)s",
        tenant_id
    )


def migrate_vm(
    mod,
    vm_url,
    auth_token,
    verify,
    payload
):
    headers = get_headers(auth_token)
    response = requests.post(
        vm_url,
        headers=headers,
        json=payload,
        verify=verify
    )
    if response.status_code != 202:
        mod.fail_json(
            msg="Failed to migrate VM",
            status_code=response.status_code,
            response=response.text,
        )
    return dict(
        changed=True,
        msg="VM migration initiated successfully",
    )


def migrate_ops(
    mod,
    connection,
    auth_token,
    tenant_id,
    verify,
    vm_id,
    payload
):
    service_name = "compute"
    endpoint = get_endpoint_url_by_service_name(
        mod,
        connection,
        service_name,
        tenant_id
    )
    url = f"{endpoint}/servers/{vm_id}/action"
    result = migrate_vm(
        mod=mod,
        vm_url=url,
        auth_token=auth_token,
        verify=verify,
        payload=payload
    )
    return result
