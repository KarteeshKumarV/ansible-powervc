#!/usr/bin/python

DOCUMENTATION = r'''
---
module: retype_volume
short_description: Retype an IBM PowerVC volume
description:
  - Performs retype operation on an existing volume.
author:
  - Karteesh Kumar Vipparapelli (@vkarteesh)
options:
  name:
    description:
      - Name of the volume.
      - Mutually exclusive with C(id).
    type: str
  id:
    description:
      - ID of the volume.
      - Mutually exclusive with C(name).
    type: str
  target_template:
    description:
      - ID of the storage template (volume type).
    type: str
  migration_policy:
    description:
      - Migration policy for retype operation.
    type: str
    default: never
    choices:
      - never
      - generic
      - on-demand
'''

EXAMPLES = r'''
- name: Retype volume using ID
  ibm.powervc.retype_volume:
    id: "VOLUME_ID"
    target_template: "STORAGE_TEMPLATE_ID"
    migration_policy: generic

- name: Retype volume using name
  ibm.powervc.retype_volume:
    name: "VOLUME_NAME"
    target_template: "STORAGE_TEMPLATE_ID"

- name: Retype volume using volume name
  ibm.powervc.retype_volume:
    name: "VOLUME_NAME"
    target_template: "STORAGE_TEMPLATE_ID"
    migration_policy: "on-demand"
'''


from ansible_collections.openstack.cloud.plugins.module_utils.openstack import OpenStackModule
from ansible_collections.ibm.powervc.plugins.module_utils.crud_retype_vol import retype_ops


class RetypeVolModule(OpenStackModule):
    argument_spec = dict(
        name=dict(type='str'),
        id=dict(type='str'),
        target_template=dict(type='str'),
        migration_policy=dict(
            type='str',
            default="never",
            choices=['never', 'generic', 'on-demand']
        ),
    )

    module_kwargs = dict(
        supports_check_mode=True,
        mutually_exclusive=[['name', 'id']],
        required_one_of=[['name', 'id']]
    )

    def run(self):
        authtoken = self.conn.auth_token
        tenant_id = self.conn.session.get_project_id()
        vol_name = self.params['name']
        vol_id = self.params['id']
        target_template_id = self.params['target_template']
        migration_policy = self.params['migration_policy']
        if vol_name:
            volume = self.conn.block_storage.find_volume(
                vol_name,
                ignore_missing=False
            )
            vol_id = volume.id

        if self.check_mode:
            self.exit_json(
                changed=True,
                msg="Retype operation would be executed"
            )

        data = {
            "os-retype": {
                "new_type": target_template_id,
                "migration_policy": migration_policy
            }
        }

        result = retype_ops(
            self,
            self.conn,
            authtoken,
            tenant_id,
            vol_id,
            data
        )

        self.exit_json(
            changed=True,
            result=result
        )


def main():
    module = RetypeVolModule()
    module()


if __name__ == '__main__':
    main()
