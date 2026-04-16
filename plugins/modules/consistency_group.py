#!/usr/bin/python

DOCUMENTATION = r'''
---
module: consistency_group
short_description: Manage PowerVC Consistency Groups
description:
  - Create, update, fetch, and delete PowerVC Storage Consistency Groups.
  - Supports adding and removing volumes during update operations.
  - Uses group ID for update and delete operations.
author:
  - Karteesh Kumar Vipparapelli (@vkarteesh)
options:
  id:
    description:
      - ID of the consistency group.
      - Required for update and delete operations.
    type: str
  name:
    description:
      - Name of the consistency group.
      - Required for create operation.
      - Can be updated.
    type: str
  description:
    description:
      - Description of the consistency group.
    type: str
  group_type:
    description:
      - Group type of the consistency group.
    type: str
  storage_templates:
    description:
      - List of storage templates (volume types).
    type: list
    elements: str
  volume_names:
    description:
      - List of volume names.
      - Mutually exclusive with C(volume_ids).
    type: list
    elements: str
  volume_ids:
    description:
      - List of volume IDs.
      - Mutually exclusive with C(volume_names).
    type: list
    elements: str
  delete_volumes:
    description:
      - Whether to delete associated volumes during group deletion.
    type: bool
    default: true
  state:
    description:
      - Desired state of the consistency group.
    type: str
    choices: [present, absent]
    default: present    
  update:
    description:
      - Update configuration for adding/removing volumes.
    type: dict
    suboptions:
      add:
        description:
          - Volumes to add.
        type: dict
        suboptions:
          volume_names:
            type: list
            elements: str
          volume_ids:
            type: list
            elements: str
      remove:
        description:
          - Volumes to remove.
        type: dict
        suboptions:
          volume_names:
            type: list
            elements: str
          volume_ids:
            type: list
            elements: str
'''

EXAMPLES = r'''

# ==========================================================
# CREATE OPERATIONS
# ==========================================================

- name: Create a Consistency Group using Volume Names
  hosts: localhost
  gather_facts: no
  tasks:
    - name: Create Consistency Group
      ibm.powervc.consistency_group:
        cloud: "CLOUD"
        name: "CG_WITH_NAMES"
        group_type: "GROUP_TYPE"
        volume_names:
          - Volume1
          - Volume2
        storage_templates:
          - TEMPLATE1
        description: "Created using volume names"
      register: output

    - debug:
        var: output


- name: Create a Consistency Group using Volume IDs
  hosts: localhost
  gather_facts: no
  tasks:
    - name: Create Consistency Group using IDs
      ibm.powervc.consistency_group:
        cloud: "CLOUD"
        name: "CG_WITH_IDS"
        group_type: "GROUP_TYPE"
        volume_ids:
          - 1111-aaaa-bbbb
          - 2222-cccc-dddd
        description: "Created using volume IDs"
      register: output

    - debug:
        var: output


- name: Create a Consistency Group using Storage Templates only
  hosts: localhost
  gather_facts: no
  tasks:
    - name: Create Consistency Group with templates
      ibm.powervc.consistency_group:
        cloud: "CLOUD"
        name: "CG_WITH_TEMPLATE"
        storage_templates:
          - TEMPLATE1
        description: "Created using storage template"
      register: output

    - debug:
        var: output


# ==========================================================
# GET OPERATIONS
# ==========================================================

- name: Get all Consistency Groups
  hosts: localhost
  gather_facts: no
  tasks:
    - name: Fetch all groups
      ibm.powervc.consistency_group:
        cloud: "CLOUD"
      register: output

    - debug:
        var: output


- name: Get specific Consistency Group by ID
  hosts: localhost
  gather_facts: no
  tasks:
    - name: Fetch specific group
      ibm.powervc.consistency_group:
        cloud: "CLOUD"
        id: "CG_ID"
      register: output

    - debug:
        var: output


# ==========================================================
# UPDATE OPERATIONS (Requires ID)
# ==========================================================

- name: Rename an existing Consistency Group
  hosts: localhost
  gather_facts: no
  tasks:
    - name: Rename CG
      ibm.powervc.consistency_group:
        cloud: "CLOUD"
        id: "CG_ID"
        name: "NEW_NAME"
      register: output

    - debug:
        var: output


- name: Update Description of a Consistency Group
  hosts: localhost
  gather_facts: no
  tasks:
    - name: Update description
      ibm.powervc.consistency_group:
        cloud: "CLOUD"
        id: "CG_ID"
        description: "Updated description"
      register: output

    - debug:
        var: output


- name: Update Name and Description together
  hosts: localhost
  gather_facts: no
  tasks:
    - name: Update both fields
      ibm.powervc.consistency_group:
        cloud: "CLOUD"
        id: "CG_ID"
        name: "UPDATED_NAME"
        description: "Updated description"
      register: output

    - debug:
        var: output


- name: Add Volumes by ID
  hosts: localhost
  gather_facts: no
  tasks:
    - name: Add volumes
      ibm.powervc.consistency_group:
        cloud: "CLOUD"
        id: "CG_ID"
        update:
          add:
            volume_ids:
              - 1111-aaaa-bbbb
      register: output

    - debug:
        var: output


- name: Remove Volumes by Name
  hosts: localhost
  gather_facts: no
  tasks:
    - name: Remove volumes
      ibm.powervc.consistency_group:
        cloud: "CLOUD"
        id: "CG_ID"
        update:
          remove:
            volume_names:
              - Volume1
      register: output

    - debug:
        var: output


- name: Add and Remove Volumes together (IDs)
  hosts: localhost
  gather_facts: no
  tasks:
    - name: Modify volumes
      ibm.powervc.consistency_group:
        cloud: "CLOUD"
        id: "CG_ID"
        update:
          add:
            volume_ids:
              - 1111-aaaa-bbbb
          remove:
            volume_ids:
              - 2222-cccc-dddd
      register: output

    - debug:
        var: output


- name: Add and Remove Volumes together (Names)
  hosts: localhost
  gather_facts: no
  tasks:
    - name: Modify volumes by names
      ibm.powervc.consistency_group:
        cloud: "CLOUD"
        id: "CG_ID"
        update:
          add:
            volume_names:
              - Volume2
          remove:
            volume_names:
              - Volume3
      register: output

    - debug:
        var: output


# ==========================================================
# DELETE OPERATIONS
# ==========================================================

- name: Delete Consistency Group (default deletes volumes)
  hosts: localhost
  gather_facts: no
  tasks:
    - name: Delete CG
      ibm.powervc.consistency_group:
        cloud: "CLOUD"
        id: "CG_ID"
        state: absent
      register: output

    - debug:
        var: output
'''

from ansible_collections.openstack.cloud.plugins.module_utils.openstack import OpenStackModule
from ansible_collections.ibm.powervc.plugins.module_utils.crud_consistency_group import (
    createcg_ops,
    updatecg_ops,
    getcg_ops,
    deletecg_ops
)


class ConsistencyGroupModule(OpenStackModule):
    argument_spec = dict(
        state=dict(type="str", choices=["present", "absent"], default="present"),
        id=dict(type='str'),
        name=dict(type='str'),
        description=dict(type='str'),
        group_type=dict(type='str'),
        storage_templates=dict(type='list', elements='str'),
        volume_names=dict(type='list', elements='str'),
        volume_ids=dict(type='list', elements='str'),
        delete_volumes=dict(type="bool", default=True),
        update=dict(
            type='dict',
            options=dict(
                add=dict(
                    type='dict',
                    options=dict(
                        volume_names=dict(type='list', elements='str'),
                        volume_ids=dict(type='list', elements='str'),
                    )
                ),
                remove=dict(
                    type='dict',
                    options=dict(
                        volume_names=dict(type='list', elements='str'),
                        volume_ids=dict(type='list', elements='str'),
                    )
                )
            )
        )
    )
    module_kwargs = dict(
        supports_check_mode=True,
        mutually_exclusive=[
            ['volume_names', 'volume_ids'],
        ]
    )

    def run(self):
        authtoken = self.conn.auth_token
        tenant_id = self.conn.session.get_project_id()
        state = self.params.get("state")
        delete_volumes = self.params.get("delete_volumes")
        group_id = self.params.get('id')
        name = self.params.get('name')
        description = self.params.get('description')
        group_type = self.params.get('group_type')
        storage_templates = self.params.get('storage_templates')
        volume_names = self.params.get('volume_names')
        volume_ids = self.params.get('volume_ids')
        update_data = self.params.get('update')

        # ==========================================================
        # DELETE
        # ==========================================================
        if state == "absent":
            if not group_id:
                self.fail_json(
                    msg="id is required when state=absent",
                    changed=False
                )
            result = deletecg_ops(
                mod=self,
                connectn=self.conn,
                authtoken=authtoken,
                tenant_id=tenant_id,
                group_id=group_id,
                delete_volumes=delete_volumes
            )
            self.exit_json(**result)
        if state == "present":
            if not group_id and not name:
                result = getcg_ops(
                    mod=self,
                    connectn=self.conn,
                    authtoken=authtoken,
                    tenant_id=tenant_id
                )
                self.exit_json(**result)
            if group_id and not (name or description or update_data or volume_names or volume_ids):
                result = getcg_ops(
                    mod=self,
                    connectn=self.conn,
                    authtoken=authtoken,
                    tenant_id=tenant_id,
                    group_id=group_id
                )
                self.exit_json(**result)
            if group_id:
                existing_group = self.conn.block_storage.get_group(group_id)
                if not existing_group:
                    self.fail_json(
                        msg=f"Consistency group with id '{group_id}' not found",
                        changed=False
                    )

                update_payload = {}
                vol_data = {}
                changed = False
                if name and name != existing_group.name:
                    update_payload["name"] = name
                    changed = True
                if description and description != existing_group.description:
                    update_payload["description"] = description
                    changed = True
                if volume_names:
                    volume_ids = [
                        self.conn.block_storage.find_volume(v, ignore_missing=False).id
                        for v in volume_names
                    ]
                if update_data:
                    add_ids = []
                    remove_ids = []
                    add_section = update_data.get("add")
                    if add_section:
                        if add_section.get("volume_names"):
                            for v in add_section.get("volume_names"):
                                resolved = self.conn.block_storage.find_volume(v, ignore_missing=False)
                                add_ids.append(resolved.id)
                        if add_section.get("volume_ids"):
                            add_ids.extend(add_section.get("volume_ids"))
                    remove_section = update_data.get("remove")
                    if remove_section:
                        if remove_section.get("volume_names"):
                            for v in remove_section.get("volume_names"):
                                resolved = self.conn.block_storage.find_volume(v, ignore_missing=False)
                                remove_ids.append(resolved.id)
                        if remove_section.get("volume_ids"):
                            remove_ids.extend(remove_section.get("volume_ids"))
                    if add_ids:
                        vol_data["add_volumes"] = ",".join(add_ids)
                        changed = True
                    if remove_ids:
                        vol_data["remove_volumes"] = ",".join(remove_ids)
                        changed = True
                if not changed:
                    self.exit_json(
                        changed=False,
                        msg="No updates required"
                    )
                if self.check_mode:
                    self.exit_json(
                        changed=True,
                        msg="Consistency group would be updated"
                    )
                result = updatecg_ops(
                    mod=self,
                    connectn=self.conn,
                    authtoken=authtoken,
                    tenant_id=tenant_id,
                    group_id=group_id,
                    update_payload=update_payload,
                    vol_data=vol_data
                )
                self.exit_json(**result)

            # ======================================================
            # CREATE
            # ======================================================
            if not name:
                self.fail_json(
                    msg="name is required for create operation",
                    changed=False
                )

            if volume_names:
                volume_ids = [
                    self.conn.block_storage.find_volume(v, ignore_missing=False).id
                    for v in volume_names
                ]

            vol_data = None
            if volume_ids:
                vol_data = {"add_volumes": ",".join(volume_ids)}

            volume_types_set = set()
            if volume_ids:
                for vid in volume_ids:
                    volume = self.conn.block_storage.get_volume(vid)
                    volume_types_set.add(volume.volume_type)
            if storage_templates:
                for vt in storage_templates:
                    volume_types_set.add(vt)
            volume_types = list(volume_types_set)
            if not volume_types:
                self.fail_json(
                    msg="At least one volume type must be provided",
                    changed=False
                )
            if self.check_mode:
                self.exit_json(
                    changed=True,
                    msg="Consistency group would be created"
                )
            result = createcg_ops(
                mod=self,
                connectn=self.conn,
                authtoken=authtoken,
                tenant_id=tenant_id,
                name=name,
                group_type=group_type,
                volume_types=volume_types,
                description=description,
                vol_data=vol_data
            )
            self.exit_json(**result)


def main():
    module = ConsistencyGroupModule()
    module()


if __name__ == '__main__':
    main()
