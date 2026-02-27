#!/usr/bin/python

DOCUMENTATION = r"""
---
module: auxiliary_volume
short_description: Manage Auxiliary Volume onboard jobs in PowerVC
description:
  - Create auxiliary volume onboard jobs.
  - Retrieve a specific auxiliary volume job by job ID.
  - List all auxiliary volume onboard jobs.
author:
    - Karteesh Kumar Vipparapelli (@vkarteesh)
options:
  job_id:
    description:
      - ID of the auxiliary volume onboard job.
    type: str
    required: false
  name:
    description:
      - Name of the auxiliary volume onboard job.
      - Required when creating a job.
    type: str
    required: false
  volumes:
    description:
      - List of volumes grouped by source project.
      - Required when creating a job.
    type: list
    elements: dict
    required: false
    suboptions:
      source_project_id:
        description:
          - UUID of the source project.
        type: str
        required: true
      aux_vols:
        description:
          - List of auxiliary volumes.
        type: list
        elements: dict
        suboptions:
          name:
            type: str
            required: true
          display_name:
            type: str
            required: false
"""

EXAMPLES = r"""

- name: Create auxiliary volume onboard job
  ibm.powervc.auxiliary_volume:
    cloud: CLOUD
    name: aux_job_01
    volumes:
      - source_project_id: "aaaaaabbbbbbccccccddddd"
        aux_vols:
          - name: aux_vol_01
  register: job_output

- name: Wait for job completion
  ibm.powervc.auxiliary_volume:
    cloud: CLOUD
    job_id: "{{ job_output.result.job_id }}"
  register: job_status
  until: job_status.result.status == "SUCCESS"
  retries: 10
  delay: 5

- name: List all jobs
  ibm.powervc.auxiliary_volume:
    cloud: CLOUD

- name: Get auxiliary volume job details
  ibm.powervc.auxiliary_volume:
    cloud: CLOUD
    job_id: "job-123456"
"""

from ansible_collections.ibm.powervc.plugins.module_utils.crud_aux_volume import (
    create_aux_vol,
    get_all_aux_vols,
    get_aux_vol_by_job,
    get_endpoint_url_by_service_name,
)
from ansible_collections.openstack.cloud.plugins.module_utils.openstack import (
    OpenStackModule,
)


class AuxVolModule(OpenStackModule):
    argument_spec = dict(
        job_id=dict(type="str"),
        name=dict(type="str"),
        volumes=dict(
            type="list",
            elements="dict",
            options=dict(
                source_project_id=dict(type="str", required=True),
                aux_vols=dict(
                    type="list",
                    elements="dict",
                    options=dict(
                        name=dict(type="str", required=True),
                        display_name=dict(type="str"),
                    ),
                ),
            ),
        ),
    )

    module_kwargs = dict(supports_check_mode=True)

    def run(self):
        authtoken = self.conn.auth_token
        tenant_id = self.conn.session.get_project_id()
        job_id = self.params.get("job_id")
        name = self.params.get("name")
        volumes = self.params.get("volumes")
        endpoint = get_endpoint_url_by_service_name(
            self, self.conn, "volume", tenant_id
        )
        # -------------------------------------------------
        # GET SPECIFIC JOB
        # -------------------------------------------------
        if job_id:
            result = get_aux_vol_by_job(
                module=self, endpoint=endpoint, authtoken=authtoken, job_id=job_id
            )
            self.exit_json(changed=False, result=result)
        # -------------------------------------------------
        # CREATE
        # -------------------------------------------------
        if name and volumes:
            if self.check_mode:
                self.exit_json(
                    changed=True, msg="Auxiliary volume onboard task would be created"
                )
            result = create_aux_vol(
                module=self,
                endpoint=endpoint,
                authtoken=authtoken,
                name=name,
                volumes=volumes,
            )
            self.exit_json(changed=True, result=result)
        # LIST ALL JOBS
        result = get_all_aux_vols(module=self, endpoint=endpoint, authtoken=authtoken)
        self.exit_json(changed=False, result=result)


def main():
    module = AuxVolModule()
    module()


if __name__ == "__main__":
    main()
