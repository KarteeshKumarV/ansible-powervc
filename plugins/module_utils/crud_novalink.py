#!/usr/bin/python

"""
This module helps in performing the registration and unregistration
of the NovaLink host.
"""

import requests

from ansible_collections.ibm.powervc.plugins.module_utils.agentic_ai.diagnostic_hook import (
    build_error_context,
    run_diagnostics
)


def get_headers(authtoken):
    return {
        "X-Auth-Token": authtoken,
        "Content-Type": "application/json"
    }


def get_endpoint_url_by_service_name(
    connectn,
    service_name,
    tenant_id
):
    """
    Get the endpoint URL for the requested service.
    """

    all_endpoints = connectn.identity.endpoints()
    services = connectn.identity.services()

    service_name_mapping = {
        service.id: service.type
        for service in services
    }

    service_id = next(
        (
            service_id
            for service_id, name in service_name_mapping.items()
            if name == service_name
        ),
        None
    )

    if service_id:

        endpoint = next(
            (
                ep
                for ep in all_endpoints
                if ep.service_id == service_id
            ),
            None
        )

        if endpoint:
            return endpoint.url.replace(
                "%(tenant_id)s",
                tenant_id
            )

        return (
            f"No endpoint found for service "
            f"'{service_name}'"
        )

    return f"No service found with the name '{service_name}'"


def _get_error_message(response):
    """
    Safely retrieve an error response.

    Some HTTP error responses may not contain valid JSON.
    """

    try:
        return str(response.json())
    except ValueError:
        return response.text


def delete_host(
    mod,
    authtoken,
    host_url,
    host_id,
    ai_diagnostics=False,
    agent=None
):
    """
    Remove the NovaLink host.
    """

    headers_scg = get_headers(authtoken)

    response = requests.delete(
        host_url,
        headers=headers_scg,
        verify=False
    )

    if response.ok:

        return dict(
            changed=True,
            msg=f"Removed the Novalink Host: {host_id}"
        )

    diagnosis = None

    if ai_diagnostics:

        error_message = _get_error_message(response)

        error_context = build_error_context(
            operation="delete_host",
            host=host_id,
            error_message=error_message,
            status_code=response.status_code
        )

        diagnosis = run_diagnostics(
            error_context,
            agent=agent
        )

    failure_message = (
        f"An unexpected error occurred: "
        f"{_get_error_message(response)}"
    )

    if diagnosis:

        mod.fail_json(
            msg=failure_message,
            ai_diagnosis=diagnosis,
            changed=False
        )

    mod.fail_json(
        msg=failure_message,
        changed=False
    )


def post_host(
    module,
    authtoken,
    host_url,
    post_data,
    ai_diagnostics=False,
    agent=None
):
    """
    Register a NovaLink host.
    """

    headers_scg = get_headers(authtoken)

    response = requests.post(
        host_url,
        headers=headers_scg,
        json=post_data,
        verify=False
    )

    if response.ok:

        return dict(
            changed=True,
            msg="Added the Host",
            result=response.json()
        )

    diagnosis = None

    if ai_diagnostics:

        host = (
            post_data
            .get("host", {})
            .get("registration", {})
            .get("access_ip")
        )

        error_message = _get_error_message(response)

        error_context = build_error_context(
            operation="register_host",
            host=host,
            error_message=error_message,
            status_code=response.status_code
        )

        diagnosis = run_diagnostics(
            error_context,
            agent=agent
        )

    failure_message = (
        f"Failed in Adding the host: "
        f"{_get_error_message(response)}"
    )

    if diagnosis:

        module.fail_json(
            msg=failure_message,
            ai_diagnosis=diagnosis,
            changed=False
        )

    module.fail_json(
        msg=failure_message,
        changed=False
    )


def put_host(
    module,
    authtoken,
    host_url,
    body,
    ai_diagnostics=False,
    agent=None
):
    """
    Update a NovaLink host.
    """

    headers_scg = get_headers(authtoken)

    response = requests.put(
        host_url,
        headers=headers_scg,
        json=body,
        verify=False
    )

    if response.ok:

        resp = response.json()

        if "private_key_data" in resp.get(
            "registration",
            {}
        ):
            resp["registration"][
                "private_key_data"
            ] = "VALUE_SPECIFIED_IN_NO_LOG_PARAMETER"

        return dict(
            changed=True,
            msg="Updated the Host",
            result=resp
        )

    diagnosis = None

    if ai_diagnostics:

        registration = body.get(
            "registration",
            {}
        )

        host = registration.get(
            "access_ip",
            "unknown"
        )

        error_message = _get_error_message(response)

        error_context = build_error_context(
            operation="update_host",
            host=host,
            error_message=error_message,
            status_code=response.status_code
        )

        diagnosis = run_diagnostics(
            error_context,
            agent=agent
        )

    failure_message = (
        f"Failed in updating host: "
        f"{_get_error_message(response)}"
    )

    if diagnosis:

        module.fail_json(
            msg=failure_message,
            ai_diagnosis=diagnosis,
            changed=False
        )

    module.fail_json(
        msg=failure_message,
        changed=False
    )


def host_ops(
    mod,
    connectn,
    authtoken,
    tenant_id,
    state,
    host_id,
    data,
    ai_diagnostics=False,
    agent=None
):
    """
    Performs the Host CRUD operations based on the requested action.
    """

    service_name = "compute"

    endpoint = get_endpoint_url_by_service_name(
        connectn,
        service_name,
        tenant_id
    )

    if state == "absent":

        if data == "uninstall_novalink":
            host_url = (
                f"{endpoint}/os-hosts/"
                f"{host_id}/uninstall"
            )
        else:
            host_url = (
                f"{endpoint}/os-hosts/"
                f"{host_id}"
            )

        result = delete_host(
            mod,
            authtoken,
            host_url,
            host_id,
            ai_diagnostics=ai_diagnostics,
            agent=agent
        )

    elif state == "present" and host_id:

        host_url = (
            f"{endpoint}/os-hosts/"
            f"{host_id}/update-registration"
        )

        result = put_host(
            mod,
            authtoken,
            host_url,
            data,
            ai_diagnostics=ai_diagnostics,
            agent=agent
        )

    elif state == "present":

        host_url = endpoint + "/os-hosts"

        result = post_host(
            mod,
            authtoken,
            host_url,
            data,
            ai_diagnostics=ai_diagnostics,
            agent=agent
        )

    return result
