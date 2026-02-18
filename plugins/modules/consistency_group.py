#!/usr/bin/python

DOCUMENTATION = r'''
---
module: consistency_group
short_description: Create and update PowerVC Consistency Groups
description:
  - Create or update PowerVC Storage Consistency Groups.
  - Supports updating name, description, and adding/removing volumes.
  - Update operations are performed using group ID.
author:
    - Karteesh Kumar Vipparapelli (@vkarteesh)
options:
  id:
    description:
      - ID of the consistency group.
      - Required for update operations.
    type: str
  name:
    description:
      - Name of the consistency group.
      - Required for create operation.
      - Can be updated during update operation.
    type: str
  description:
    description:
      - Description of the consistency group.
      - Can be updated during update operation.
    type: str
  group_type:
    description:
      - Group type of the consistency group.
      - Required during create operation.
    type: str
  storage_template:
    description:
      - List of storage templates (volume types) to associate during create.
      - Combined with volume types derived from provided volumes.
    type: list
    elements: str
  volume_name:
    description:
      - List of volume names to attach during create operation.
      - Mutually exclusive with C(volume_id).
    type: list
    elements: str
  volume_id:
    description:
      - List of volume IDs to attach during create operation.
      - Mutually exclusive with C(volume_name).
    type: list
    elements: str
  update:
    description:
      - Modify an existing consistency group.
      - Allows adding and/or removing volumes.
      - Both C(add) and C(remove) sections are optional.
    type: dict
    suboptions:
      add:
        description:
          - Volumes to add to the consistency group.
        type: dict
        suboptions:
          volume_name:
            description:
              - List of volume names to add.
            type: list
            elements: str
          volume_id:
            description:
              - List of volume IDs to add.
            type: list
            elements: str
      remove:
        description:
          - Volumes to remove from the consistency group.
        type: dict
        suboptions:
          volume_name:
            description:
              - List of volume names to remove.
            type: list
            elements: str
          volume_id:
            description:
              - List of volume IDs to remove.
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
    - name: Create a Consistency Group
      ibm.powervc.consistency_group:
        cloud: "CLOUD"
        name: "CONSISTENCY_GROUP_NAME"
        group_type: "GROUP_TYPE_NAME"
        volume_name:
          - Volume_Name1
          - Volume_Name2
        storage_template:
          - TEMPLATE_TYPE
        description: "CONSISTENCY_GROUP DESCRIPTION"
      register: output

    - debug:
        var: output


- name: Create a Consistency Group using Volume IDs
  hosts: localhost
  gather_facts: no
  tasks:
    - name: Create CG using Volume IDs
      ibm.powervc.consistency_group:
        cloud: "CLOUD"
        name: "CG_USING_IDS"
        group_type: "GROUP_TYPE_NAME"
        volume_id:
          - 1111-aaaa-bbbb-cccc
          - 2222-dddd-eeee-ffff
        description: "Created using volume IDs"
      register: output

    - debug:
        var: output


- name: Create a Consistency Group using Storage Template
  hosts: localhost
  gather_facts: no
  tasks:
    - name: Create CG with storage template
      ibm.powervc.consistency_group:
        cloud: "CLOUD"
        name: "CG_STORAGE_TEMPLATE"
        storage_template:
          - TEMPLATE_TYPE
        description: "CG created using storage template"
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
        name: "NEW_CG_NAME"
      register: output

    - debug:
        var: output


- name: Update Description of a Consistency Group
  hosts: localhost
  gather_facts: no
  tasks:
    - name: Update CG description
      ibm.powervc.consistency_group:
        cloud: "CLOUD"
        id: "CG_ID"
        description: "Updated CG description"
      register: output

    - debug:
        var: output.result


- name: Rename and Update Description Together
  hosts: localhost
  gather_facts: no
  tasks:
    - name: Update name and description
      ibm.powervc.consistency_group:
        cloud: "CLOUD"
        id: "CG_ID"
        name: "RENAMED_CG"
        description: "Updated description"
      register: output

    - debug:
        var: output

- name: Remove and Add Volumes by ID
  hosts: localhost
  gather_facts: no
  tasks:
    - name: Remove and Add volume Names
      ibm.powervc.consistency_group:
        cloud: "CLOUD"
        id: "CG_ID"
        update:
            add:
              volume_name:
                  - 1111-aaaa-bbbb-cccc
                  - 2222-aaaa-bbbb-cccc
            remove:
              volume_name:
                  - 3333-aaaa-bbbb-cccc
                  - 4444-aaaa-bbbb-cccc
      register: output

    - debug:
        var: output

- name: Remove and Add Volumes by Name
  hosts: localhost
  gather_facts: no
  tasks:
    - name: Remove and Add volume Names
      ibm.powervc.consistency_group:
        cloud: "CLOUD"
        id: "CG_ID"
        update:
            add:
              volume_name:
                  - TestVol1
                  - TestVol2
            remove:
              volume_name:
                  - TestVol3
                  - TestVol3
      register: output

    - debug:
        var: output



- name: Add Volumes by ID
  hosts: localhost
  gather_facts: no
  tasks:
    - name: Add volume IDs
      ibm.powervc.consistency_group:
        cloud: "CLOUD"
        id: "CG_ID"
        update:
            add:
              volume_id:
                  - 4444-dddd-eeee-ffff
      register: output

    - debug:
        var: output


- name: Remove Volumes by Names
  hosts: localhost
  gather_facts: no
  tasks:
    - name: Remove volume by Names
      ibm.powervc.consistency_group:
        cloud: "CLOUD"
        id: "CG_ID"
        update:
          remove:
            volume_name:
              - 3333-aaaa-bbbb-cccc
      register: output

    - debug:
        var: output.result

'''


from ansible_collections.openstack.cloud.plugins.module_utils.openstack import OpenStackModule
from ansible_collections.ibm.powervc.plugins.module_utils.crud_consistency_group import (
    createcg_ops,
    updatecg_ops
)


class ConsistencyGroupModule(OpenStackModule):

    argument_spec = dict(
        id=dict(type='str'),  # Required for update
        name=dict(type='str'),
        description=dict(type='str'),
        group_type=dict(type='str'),

        storage_template=dict(type='list', elements='str'),
        volume_name=dict(type='list', elements='str'),
        volume_id=dict(type='list', elements='str'),
        update=dict(
                type='dict',
                options=dict(
                        add=dict(
                                type='dict',
                                options=dict(
                                        volume_name=dict(type='list', elements='str'),
                                        volume_id=dict(type='list', elements='str'),
                                )
                        ),
                        remove=dict(
                                type='dict',
                                options=dict(
                                        volume_name=dict(type='list', elements='str'),
                                        volume_id=dict(type='list', elements='str'),
                                )
                        )
                )
        )

    )

    module_kwargs = dict(
        supports_check_mode=True,
        mutually_exclusive=[
            ['volume_name', 'volume_id'],
        ]
    )

    def run(self):

        authtoken = self.conn.auth_token
        tenant_id = self.conn.session.get_project_id()

        group_id = self.params.get('id')
        name = self.params.get('name')
        description = self.params.get('description')
        group_type = self.params.get('group_type')
        storage_template = self.params.get('storage_template')
        volume_name = self.params.get('volume_name')
        volume_id = self.params.get('volume_id')
        update_data = self.params.get('update')
        # ==========================================================
        # UPDATE OPERATION (If ID is provided)
        # ==========================================================
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

            # Name update
            if name and name != existing_group.name:
                update_payload["name"] = name
                changed = True

            # Description update
            if description and description != existing_group.description:
                update_payload["description"] = description
                changed = True

            # Resolve volume names
            if volume_name:
                volume_id = [
                    self.conn.block_storage.find_volume(v, ignore_missing=False).id
                    for v in volume_name
                ]

            # Volume operations
            if update_data:
                add_ids = []
                remove_ids = []

                add_section = update_data.get("add")

                if add_section:

                        # Resolve volume_name
                        if add_section.get("volume_name"):
                                for v in add_section.get("volume_name"):
                                        resolved = self.conn.block_storage.find_volume(
                                                v, ignore_missing=False
                                        )
                                        add_ids.append(resolved.id)

                        # Direct volume_id
                        if add_section.get("volume_id"):
                                add_ids.extend(add_section.get("volume_id"))

                remove_section = update_data.get("remove")

                if remove_section:

                        # Resolve volume_name
                        if remove_section.get("volume_name"):
                                for v in remove_section.get("volume_name"):
                                        resolved = self.conn.block_storage.find_volume(
                                                v, ignore_missing=False
                                        )
                                        remove_ids.append(resolved.id)

                        # Direct volume_id
                        if remove_section.get("volume_id"):
                                remove_ids.extend(remove_section.get("volume_id"))

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

            self.exit_json(changed=True, result=result)

        # ==========================================================
        # CREATE OPERATION
        # ==========================================================
        else:

            if not name:
                self.fail_json(
                    msg="name is required for create operation",
                    changed=False
                )

            existing_group = self.conn.block_storage.find_group(
                name,
                ignore_missing=True
            )

            if existing_group:
                self.exit_json(
                    changed=False,
                    msg=f"Consistency Group '{name}' already exists"
                )

            # Resolve volume names
            if volume_name:
                volume_id = [
                    self.conn.block_storage.find_volume(v, ignore_missing=False).id
                    for v in volume_name
                ]

            vol_data = None
            if volume_id:
                vol_string = ",".join(volume_id)
                vol_data = {"add_volumes": vol_string}

            # Collect volume types
            volume_types_set = set()

            if volume_id:
                for vid in volume_id:
                    volume = self.conn.block_storage.get_volume(vid)
                    volume_types_set.add(volume.volume_type)

            if storage_template:
                for vt in storage_template:
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

            self.exit_json(changed=True, result=result)


def main():
    module = ConsistencyGroupModule()
    module()


if __name__ == '__main__':
    main()
