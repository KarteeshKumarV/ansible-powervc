#!/usr/bin/python

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'PowerVC'}


DOCUMENTATION = '''
---
module: resize_volume
author:
    - Karteesh Kumar Vipparapelli (@vkarteesh)
short_description: Performs the Resize operations on the Volume.
description:
  - This playbook helps in performing the volume operations on the Volume provided.
options:
  name:
    description:
      - Name of the Volume
    type: str
  id:
    description:
      - ID of the Volume
    type: str
  storage_template:
    description:
      - ID of the Host
    type: str
  migration_policy:
    description:
      - ID of the Host
    type: str

'''

EXAMPLES = '''
  - name: Volume Resize Playbook using Volume Name
    hosts: localhost
    gather_facts: no
    vars:
     auth:
      auth_url: https://<POWERVC>:5000/v3
      project_name: PROJECT-NAME
      username: USERID
      password: PASSWORD
      project_domain_name: PROJECT_DOMAIN_NAME
      user_domain_name: USER_DOMAIN_NAME
    tasks:
       - name: Perform Resize Volume Operations using Volume Name
         ibm.powervc.resize_volume:
            auth: "{{ auth }}"
            id: "VM_ID"
            storage_template: "STORAGE_TEMPLATE"
            migration_policy: "MIGRATION_POLICY_TYPE"
            validate_certs: no
         register: result
       - debug:
            var: result

  - name: Volume Resize Playbook using Volume ID
    hosts: localhost
    gather_facts: no
    tasks:
       - name: Perform Volume Resize Operations using Volume ID
         ibm.powervc.resize_volume:
            cloud: "CLOUDNAME"
            id: "VM_ID"
            storage_template: "STORAGE_TEMPLATE"
            migration_policy: "MIGRATION_POLICY_TYPE"
            validate_certs: no
         register: result
       - debug:
            var: result
'''


from ansible_collections.openstack.cloud.plugins.module_utils.openstack import OpenStackModule
from ansible_collections.ibm.powervc.plugins.module_utils.crud_retype_vol import retype_ops


class RetypeVolModule(OpenStackModule):
    argument_spec = dict(
        name=dict(),
        id=dict(),
        migration_policy=dict(default="never", choices=['never', 'generic', 'on-demand']),
        storage_template=dict(required=True),
    )
    module_kwargs = dict(
        supports_check_mode=True,
        mutually_exclusive=[
            ['name', 'id'],
        ],
    required_one_of=[
            ['name', 'id'],
        ]
    )

    def run(self):
        authtoken = self.conn.auth_token
        tenant_id = self.conn.session.get_project_id()
        vol_name = self.params['name']
        vol_id = self.params['id']
        storage_template = self.params['storage_template']
        migration_policy = self.params['migration_policy']
        if vol_name:
            vol_id = self.conn.block_storage.find_volume(vol_name, ignore_missing=False).id
        if storage_template:
            storage_template_id = self.conn.block_storage.find_type(storage_template, ignore_missing=False).id
        try:
            data = {"os-retype":{"new_type": storage_template_id, "migration_policy": migration_policy}}
            res = retype_ops(self, self.conn, authtoken, tenant_id, vol_id, data)
            self.exit_json(changed=True, result=res)
        except Exception as e:
            self.fail_json(msg=f"An unexpected error occurred: {str(e)}", changed=True)


def main():
    module = RetypeVolModule()
    module()


if __name__ == '__main__':
    main()
