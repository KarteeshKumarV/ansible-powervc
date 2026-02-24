#!/usr/bin/python

"""
This module performs the Onboard Auxilary Volume operations
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
    service_name_mapping = {
        service.id: service.type for service in services
    }
    service_id = next(
        (sid for sid, name in service_name_mapping.items()
         if name == service_name),
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


def wait_for_job_completion(module, job_url, headers, job_id):
    timeout_seconds = 720
    interval = 40
    elapsed = 0
    last_status = None
    last_progress = None
    while elapsed < timeout_seconds:
        response = requests.get(
            job_url,
            headers=headers,
            verify=False,
            timeout=30
        )
        if not response.ok:
            module.fail_json(
                msg=f"Failed to fetch onboard job: {response.json()}",
                changed=False
            )
        job_data = response.json().get("onboard-aux-volumes", {})
        status = job_data.get("status")
        progress = job_data.get("progress")
        last_status = status
        last_progress = progress
        module.debug(
            f"Polling job {job_id}: status={status}, progress={progress}%"
        )
        if status == "SUCCESS":
            return job_data
        if status in ["FAILED", "REVERTED", "ERROR"]:
            module.fail_json(
                msg=f"Onboard job '{job_id}' failed with status '{status}'",
                details=job_data,
                changed=False
            )
        time.sleep(interval)
        elapsed += interval

    module.fail_json(
        msg=(
            f"Timeout waiting for onboard job '{job_id}'. "
            f"Last known status: {last_status}, "
            f"progress: {last_progress}%"
        ),
        changed=False
    )


def create_aux_vol(module, endpoint, authtoken,
                   name, volumes):
    headers = get_headers(authtoken)
    onboard_url = f"{endpoint}/onboard"
    payload = {
        "onboard-volumes": {
            "name": name,
            "volumes": volumes
        }
    }
    response = requests.post(
        onboard_url,
        headers=headers,
        json=payload,
        verify=False,
        timeout=30
    )
    if not response.ok:
        module.fail_json(
            msg=f"Failed to create aux volume onboard task: {response.json()}",
            changed=False
        )
    job_id = response.json().get(
        "onboard-volumes", {}
    ).get("job_id")
    if not job_id:
        module.fail_json(
            msg="Job ID not returned from onboard API",
            changed=False
        )
    job_url = f"{onboard_url}/{job_id}"
    return wait_for_job_completion(
        module,
        job_url,
        headers,
        job_id
    )


def get_aux_vol_by_job(module, endpoint,
                       authtoken, job_id):
    headers = get_headers(authtoken)
    job_url = f"{endpoint}/onboard/{job_id}"
    response = requests.get(
        job_url,
        headers=headers,
        verify=False,
        timeout=30
    )
    if not response.ok:
        module.fail_json(
            msg=f"Failed to fetch aux volume job: {response.json()}",
            changed=False
        )
    return response.json().get("onboard-aux-volumes", {})


def get_all_aux_vols(module, endpoint, authtoken):
    headers = get_headers(authtoken)
    onboard_url = f"{endpoint}/onboard"
    response = requests.get(
        onboard_url,
        headers=headers,
        verify=False,
        timeout=30
    )
    if not response.ok:
        module.fail_json(
            msg=f"Failed to fetch aux volume jobs: {response.json()}",
            changed=False
        )
    return response.json()
