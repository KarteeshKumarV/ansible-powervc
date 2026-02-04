#!/usr/bin/python

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'PowerVC'}


DOCUMENTATION = '''
---
module: consistency_group
author:
    - Karteesh Kumar Vipparapelli (@vkarteesh)
consistency_group
short_description: Create a storage consistency group
description:
  - This module creates a consistency group.
  - Volumes can be specified either by name or by ID.
options:
  name:
    description:
      - Name of the consistency group to be created.
    required: true
    type: str
  storage_template:
    description:
      - Name of the storage template.
    required: true
    type: str
  volume_name:
    description:
      - List of volume names to be added to the consistency group.
    type: list
    elements: str
  volume_id:
    description:
      - List of volume IDs to be added to the consistency group.
    type: list
    elements: str
  group_type:
    description:
      - Type of the consistency group.
    type: str
    default: default_group_type_grs
  description:
    description:
      - Description of the consistency group.
    required: false
    type: str

'''

EXAMPLES = '''
  - name: Create a Consistency Group using Volume Names
    hosts: localhost
    gather_facts: no
    tasks:
       - name: Create a Consistency Group
         ibm.powervc.consistency_group:
            cloud: "CLOUD"
            name: "CONSISTENCY_GROUP_NAME"
            volume_name: ["Volume_Name1", "Volume_Name2"]
            storage_template: "STORAGE_TEMPLATE"
            description: "CONSISTENCY_GROUP DESCRIPTION"
            validate_certs: no
         register: output
       - debug:
            var: output.result

  - name: Create a Consistency Group using Volume IDs
    hosts: localhost
    gather_facts: no
    tasks:
       - name: Create a Consistency Group
         ibm.powervc.consistency_group:
            cloud: "CLOUD"
            name: "CONSISTENCY_GROUP_NAME"
            volume_id: ["Volume_ID1", "Volume_ID2"]
            storage_template: "STORAGE_TEMPLATE"
            description: "CONSISTENCY_GROUP DESCRIPTION"
            validate_certs: no
         register: output
       - debug:
            var: output.result

'''

from ansible_collections.openstack.cloud.plugins.module_utils.openstack import OpenStackModule
from ansible_collections.ibm.powervc.plugins.module_utils.crud_consistency_group import createcg_ops


class CreateCGModule(OpenStackModule):
    argument_spec = dict(
        name=dict(required=True),
        storage_template=dict(required=True),
        volume_name=dict(type='list'),
        volume_id=dict(type='list'),
        group_type=dict(default="default_group_type_grs"),
        description=dict(required=False),
    )
    module_kwargs = dict(
        supports_check_mode=True,
        mutually_exclusive=[
            ['volume_name', 'volume_id'],
        ],
        required_one_of=[
            ['volume_name', 'volume_id'],
        ]
    )

    def run(self):
        authtoken = self.conn.auth_token
        tenant_id = self.conn.session.get_project_id()
        name = self.params['name']
        storage_template = self.params['storage_template']
        group_type = self.params['group_type']
        description = self.params['description']
        vol_name = self.params['volume_name']
        vol_id = self.params['volume_id']
        if vol_name:
            vol_id = []
            for vname in vol_name:
                vol_id.append(self.conn.block_storage.find_volume(vname, ignore_missing=False).id)
        try:
            vol_data = ",".join(vol_id)
            vol_data = {"group": {"add_volumes": vol_data}}
            res = createcg_ops(self, self.conn, authtoken, tenant_id, name, vol_data, group_type, storage_template, description)
            self.exit_json(changed=True, result=res)
        except Exception as e:
            self.fail_json(msg=f"An unexpected error occurred: {str(e)}", changed=True)


def main():
    module = CreateCGModule()
    module()


if __name__ == '__main__':
    main()
