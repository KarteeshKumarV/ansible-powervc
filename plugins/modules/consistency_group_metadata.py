#!/usr/bin/python

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'PowerVC'
}

DOCUMENTATION = r'''
---
module: consistency_group_update
short_description: Update a storage consistency group
description:
  - Updates an existing storage consistency group.
  - Volumes can be added or removed.
  - Volumes can be specified either by name or by ID.
  - Volume update is optional.

author:
  - Karteesh Kumar Vipparapelli (@vkarteesh)

options:
  id:
    description:
      - ID of the consistency group to update.
    required: true
    type: str

  name:
    description:
      - Name of the consistency group.
    required: false
    type: str

  description:
    description:
      - Description of the consistency group.
    required: false
    type: str

  volume:
    description:
      - Volume update specification.
    required: false
    type: dict
    suboptions:
      update:
        description:
          - Operation to perform.
        type: str
        required: true
        choices:
          - add
          - remove
      name:
        description:
          - List of volume names.
          - Required if C(update=add/remove) and C(id) not provided.
        type: list
        elements: str
      id:
        description:
          - List of volume IDs.
          - Required if C(update=add/remove) and C(name) not provided.
        type: list
        elements: str
'''

EXAMPLES = r'''
- name: Add volumes using names
  hosts: localhost
  gather_facts: no
  tasks:
    - name: Add volumes to CG
      ibm.powervc.consistency_group_update:
        cloud: CLOUD
        id: "CG_ID"
        volume:
          update: add
          name: ["Vol1", "Vol2"]
      register: result

    - debug:
        var: result.result


- name: Remove volumes using IDs
  hosts: localhost
  gather_facts: no
  tasks:
    - name: Remove volumes from CG
      ibm.powervc.consistency_group_update:
        cloud: CLOUD
        id: "CG_ID"
        volume:
          update: remove
          id: ["vol-id-1", "vol-id-2"]
      register: result

    - debug:
        var: result.result


- name: Update only description
  hosts: localhost
  gather_facts: no
  tasks:
    - name: Update description only
      ibm.powervc.consistency_group_update:
        cloud: CLOUD
        id: "CG_ID"
        description: "Updated description"
'''

from ansible_collections.openstack.cloud.plugins.module_utils.openstack import OpenStackModule
from ansible_collections.ibm.powervc.plugins.module_utils.crud_consistency_group_update import updatecg_ops


class UpdateCGModule(OpenStackModule):

    argument_spec = dict(
        id=dict(type='str', required=True),
        name=dict(type='str'),
        description=dict(type='str'),
        volume=dict(
            type='dict',
            options=dict(
                update=dict(type='str', choices=['add', 'remove'], required=True),
                name=dict(type='list', elements='str'),
                id=dict(type='list', elements='str'),
            )
        )
    )

    module_kwargs = dict(
        supports_check_mode=True,
    )

    def run(self):
        authtoken = self.conn.auth_token
        tenant_id = self.conn.session.get_project_id()

        cg_id = self.params.get('id')
        name = self.params.get('name')
        description = self.params.get('description')
        volume = self.params.get('volume')

        vol_data = None

        # -------------------------
        # Volume Handling (Optional)
        # -------------------------
        if volume:
            update_type = volume.get("update")
            name_list = volume.get("name")
            id_list = volume.get("id")

            # Validation
            if not name_list and not id_list:
                self.fail_json(
                    msg="Either volume.name or volume.id must be provided"
                )

            if name_list and id_list:
                self.fail_json(
                    msg="Provide either volume.name or volume.id, not both"
                )

            vol_ids = []

            # Convert names to IDs if needed
            if name_list:
                for vname in name_list:
                    vol = self.conn.block_storage.find_volume(
                        vname,
                        ignore_missing=False
                    )
                    vol_ids.append(vol.id)

            if id_list:
                vol_ids = id_list

            vol_string = ",".join(vol_ids)

            if update_type == "add":
                vol_data = {"add_volumes": vol_string}
            else:
                vol_data = {"remove_volumes": vol_string}

        # -------------------------
        # Check Mode Support
        # -------------------------
        if self.check_mode:
            self.exit_json(
                changed=bool(name or description or vol_data),
                msg="Check mode: no changes applied"
            )                    

        try:
            res = updatecg_ops(self, self.conn, authtoken, tenant_id, cg_id, name, description, vol_data)
            self.exit_json(
                changed=True,
                result=res
            )

        except Exception as e:
            self.fail_json(
                msg=f"An unexpected error occurred: {str(e)}",
                changed=False
            )


def main():
    module = UpdateCGModule()
    module()


if __name__ == '__main__':
    main()

