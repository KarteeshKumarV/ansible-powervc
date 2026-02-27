#!/usr/bin/python

"""
CRUD operations for Auxiliary Volume onboard jobs
"""

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
    service_name_mapping = {service.id: service.type for service in services}
    service_id = next(
        (sid for sid, name in service_name_mapping.items() if name == service_name),
        None,
    )
    if not service_id:
        mod.fail_json(
            msg=f"No service found with the name '{service_name}'", changed=False
        )
    endpoint = next((ep for ep in all_endpoints if ep.service_id == service_id), None)
    if not endpoint:
        mod.fail_json(
            msg=f"No endpoint found for service '{service_name}'", changed=False
        )
    return endpoint.url.replace("%(tenant_id)s", tenant_id)


# ---------------------------------------------------------
# CREATE AUXILIARY VOLUME ONBOARD JOB
# ---------------------------------------------------------


def create_aux_vol(module, endpoint, authtoken, name, volumes):
    headers = get_headers(authtoken)
    onboard_url = f"{endpoint}/onboard"
    payload = {"onboard-volumes": {"name": name, "volumes": volumes}}
    response = requests.post(
        onboard_url, headers=headers, json=payload, verify=False, timeout=30
    )
    if not response.ok:
        module.fail_json(
            msg="Failed to create auxiliary volume onboard task",
            response=response.text,
            status_code=response.status_code,
            changed=False,
        )
    data = response.json()
    job_id = data.get("onboard-volumes", {}).get("job_id")
    if not job_id:
        module.fail_json(
            msg="Job ID not returned from onboard API", response=data, changed=False
        )
    return {"job_id": job_id, "status": "SUBMITTED"}


# ---------------------------------------------------------
# GET SPECIFIC JOB
# ---------------------------------------------------------


def get_aux_vol_by_job(module, endpoint, authtoken, job_id):
    headers = get_headers(authtoken)
    job_url = f"{endpoint}/onboard/{job_id}"
    response = requests.get(job_url, headers=headers, verify=False, timeout=30)
    if not response.ok:
        module.fail_json(
            msg="Failed to fetch auxiliary volume job",
            response=response.text,
            status_code=response.status_code,
            changed=False,
        )
    return response.json().get("onboard-aux-volumes", {})


# ---------------------------------------------------------
# LIST ALL JOBS
# ---------------------------------------------------------


def get_all_aux_vols(module, endpoint, authtoken):
    headers = get_headers(authtoken)
    onboard_url = f"{endpoint}/onboard"
    response = requests.get(onboard_url, headers=headers, verify=False, timeout=30)
    if not response.ok:
        module.fail_json(
            msg="Failed to fetch auxiliary volume jobs",
            response=response.text,
            status_code=response.status_code,
            changed=False,
        )
    return response.json()
