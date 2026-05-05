#!/usr/bin/python

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'PowerVC'
}

DOCUMENTATION = r'''
---
module: migrate_vm
short_description: Perform live or cold VM migration in IBM PowerVC
description:
  - Supports live migration.
  - Supports cold migration.
  - Supports migration across host groups using ignore_az.
author:
    - Karteesh Kumar Vipparapelli (@vkarteesh)
options:
  name:
    description:
      - Name of the virtual machine to migrate.
    type: str
  id:
    description:
      - UUID of the virtual machine to migrate.
    type: str
  host:
    description:
      - MTMS of the arget compute host where the virtual machine will be migrated.
    type: str
    required: true
  migration_type:
    description:
      - Type of migration to perform.
      - C(live) performs live migration.
      - C(cold) performs cold migration.
    choices:
      - live
      - cold
    type: str
  ignore_az:
    description:
      - Allows migration across availability zones or host groups.
    type: bool
    default: false
  block_migration:
    description:
      - Enable block migration during live migration.
      - Applicable only for live migration.
    type: bool
    default: false
  disk_over_commit:
    description:
      - Allow disk overcommit during live migration.
      - Applicable only for live migration.
    type: bool
    default: true
  force:
    description:
      - Force live migration operation.
      - Applicable only for live migration.
    type: bool
    default: false
'''

EXAMPLES = r'''
---
- name: Live migrate VM using VM name
  hosts: localhost
  gather_facts: false
  tasks:
    - name: Perform live migration using VM name
      ibm.powervc.migrate_vm:
        cloud: powervc
        name: test-vm
        host: 828384A_215ABCD
        migration_type: live

- name: Live migrate VM using VM ID
  hosts: localhost
  gather_facts: false
  tasks:
    - name: Perform live migration using VM ID
      ibm.powervc.migrate_vm:
        cloud: powervc
        id: "8f4d9b4f-1234-5678-abcd-123456789abc"
        host: 828384A_215ABCD
        migration_type: live

- name: Live migrate VM with block migration
  hosts: localhost
  gather_facts: false
  tasks:
    - name: Perform block live migration
      ibm.powervc.migrate_vm:
        cloud: powervc
        name: test-vm
        host: 828384A_215ABCD
        migration_type: live
        block_migration: true

- name: Live migrate VM across host groups
  hosts: localhost
  gather_facts: false
  tasks:
    - name: Perform live migration across host groups
      ibm.powervc.migrate_vm:
        cloud: powervc
        name: test-vm
        host: 828384A_215ABCD
        migration_type: live
        ignore_az: true

- name: Cold migrate VM
  hosts: localhost
  gather_facts: false
  tasks:
    - name: Perform cold migration
      ibm.powervc.migrate_vm:
        cloud: powervc
        name: test-vm
        host: 828384A_215ABCD
        migration_type: cold

- name: Cold migrate VM across host groups
  hosts: localhost
  gather_facts: false
  tasks:
    - name: Perform cold migration across host groups
      ibm.powervc.migrate_vm:
        cloud: powervc
        name: test-vm
        host: 828384A_216ABCD
        migration_type: cold
        ignore_az: true

- name: Force live migration
  hosts: localhost
  gather_facts: false
  tasks:
    - name: Perform forced live migration
      ibm.powervc.migrate_vm:
        cloud: powervc
        name: test-vm
        host: 828384A_216ABCD
        migration_type: live
        force: true

- name: Live migration with disk overcommit
  hosts: localhost
  gather_facts: false
  tasks:
    - name: Perform live migration with disk overcommit
      ibm.powervc.migrate_vm:
        cloud: powervc
        name: test-vm
        host: 828384A_217ABCD
        migration_type: live
        disk_over_commit: true
'''

from ansible_collections.openstack.cloud.plugins.module_utils.openstack import OpenStackModule
from ansible_collections.ibm.powervc.plugins.module_utils.crud_migrate import migrate_ops


class MigrateVMModule(OpenStackModule):
    argument_spec = dict(
        name=dict(type='str'),
        id=dict(type='str'),
        host=dict(
            type='str',
            required=True
        ),
        migration_type=dict(
            type='str',
            choices=['live', 'cold']
        ),
        ignore_az=dict(
            type='bool',
            default=False
        ),
        block_migration=dict(
            type='bool',
            default=False
        ),
        disk_over_commit=dict(
            type='bool',
            default=True
        ),
        force=dict(
            type='bool',
            default=False
        ),
    )
    module_kwargs = dict(
        supports_check_mode=True,
        mutually_exclusive=[
            ['name', 'id']
        ]
    )

    def run(self):
        authtoken = self.conn.auth_token
        tenant_id = self.conn.session.get_project_id()
        vm_name = self.params['name']
        vm_id = self.params['id']
        host = self.params['host']
        migration_type = self.params['migration_type']
        ignore_az = self.params['ignore_az']
        validate_certs = self.params.get("validate_certs")
        if validate_certs is False:
            self.conn.session.verify = False
        verify = self.conn.session.verify
        if vm_name:
            server = self.conn.compute.find_server(
                vm_name,
                ignore_missing=False
            )
            vm_id = server.id
        try:
            # LIVE MIGRATION
            if migration_type == "live":
                payload = {
                    "os-migrateLive": {
                        "host": host,
                        "block_migration": self.params[
                            'block_migration'
                        ],
                        "disk_over_commit": self.params[
                            'disk_over_commit'
                        ],
                        "force": self.params['force'],
                        "ignore_az": ignore_az
                    }
                }

            # COLD MIGRATION
            elif migration_type == "cold":
                payload = {
                    "migrate": {
                        "host": host,
                        "ignore_az": ignore_az
                    }
                }
            result = migrate_ops(
                mod=self,
                connection=self.conn,
                auth_token=authtoken,
                tenant_id=tenant_id,
                verify=verify,
                vm_id=vm_id,
                payload=payload
            )
            self.exit_json(
                changed=True,
                result=result
            )

        except Exception as ex:
            self.fail_json(
                msg=str(ex),
                changed=False
            )


def main():
    module = MigrateVMModule()
    module()


if __name__ == '__main__':
    main()
