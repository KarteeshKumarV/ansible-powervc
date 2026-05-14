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
  - Supports live and cold VM migration in IBM PowerVC.
  - Live migration moves a running virtual machine.
  - Cold migration moves a powered off virtual machine.
  - Supports migration to a specified host or placement policy based host selection.
  - Supports cross host-group migration using ignore_az.
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
      - MTMS of the target compute host.
      - If not specified, the destination host is selected using placement policy.
      - Required when ignore_az is set to true.
    type: str
  type:
    description:
      - Type of migration to perform.
      - C(live) migrates a running virtual machine.
      - C(cold) migrates a powered off virtual machine.
    choices:
      - live
      - cold
    type: str
    required: true
  ignore_az:
    description:
      - Allows migration across availability zones or host groups.
    type: bool
    default: false
  block_migration:
    description:
      - Enables block migration during live migration.
      - Applicable only for live migration.
    type: bool
    default: false
  disk_over_commit:
    description:
      - Enables disk overcommit during live migration.
      - Applicable only for live migration.
    type: bool
    default: true
  force:
    description:
      - Forces live migration without scheduler verification.
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
        type: live

- name: Live migrate VM using VM ID
  hosts: localhost
  gather_facts: false
  tasks:
    - name: Perform live migration using VM ID
      ibm.powervc.migrate_vm:
        cloud: powervc
        id: "8f4d9b4f-1234-5678-abcd-123456789abc"
        type: live

- name: Live migrate VM with target host
  hosts: localhost
  gather_facts: false
  tasks:
    - name: Perform live migration to specific host
      ibm.powervc.migrate_vm:
        cloud: powervc
        name: test-vm
        host: 828384A_215ABCD
        type: live

- name: Live migrate VM with placement policy
  hosts: localhost
  gather_facts: false
  tasks:
    - name: Perform live migration using placement policy
      ibm.powervc.migrate_vm:
        cloud: powervc
        name: test-vm
        type: live

- name: Live migrate VM with block migration
  hosts: localhost
  gather_facts: false
  tasks:
    - name: Perform block live migration
      ibm.powervc.migrate_vm:
        cloud: powervc
        name: test-vm
        host: 828384A_215ABCD
        type: live
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
        type: live
        ignore_az: true

- name: Cold migrate VM
  hosts: localhost
  gather_facts: false
  tasks:
    - name: Perform cold migration
      ibm.powervc.migrate_vm:
        cloud: powervc
        name: test-vm
        type: cold

- name: Cold migrate VM with placement policy
  hosts: localhost
  gather_facts: false
  tasks:
    - name: Perform cold migration using placement policy
      ibm.powervc.migrate_vm:
        cloud: powervc
        name: test-vm
        type: cold

- name: Cold migrate VM across host groups
  hosts: localhost
  gather_facts: false
  tasks:
    - name: Perform cold migration across host groups
      ibm.powervc.migrate_vm:
        cloud: powervc
        name: test-vm
        host: 828384A_216ABCD
        type: cold
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
        type: live
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
        type: live
        disk_over_commit: true
'''

from ansible_collections.openstack.cloud.plugins.module_utils.openstack import OpenStackModule
from ansible_collections.ibm.powervc.plugins.module_utils.crud_migrate import migrate_ops


class MigrateVMModule(OpenStackModule):
    argument_spec = dict(
        name=dict(type='str'),
        id=dict(type='str'),
        host=dict(type='str'),
        type=dict(
            type='str',
            choices=['live', 'cold'],
            required=True
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
        migration_type = self.params['type']
        ignore_az = self.params['ignore_az']
        block_migration = self.params['block_migration']
        disk_over_commit = self.params['disk_over_commit']
        force = self.params['force']
        validate_certs = self.params.get("validate_certs")
        if validate_certs is False:
            self.conn.session.verify = False
        verify = self.conn.session.verify
        if ignore_az and not host:
            self.fail_json(
                msg="host is mandatory when ignore_az=True",
                changed=False
            )
        if vm_name:
            server = self.conn.compute.find_server(
                vm_name,
                ignore_missing=False
            )
            vm_id = server.id
        vm_identifier = vm_name if vm_name else vm_id
        try:
            if migration_type == "live":
                payload = {
                    "os-migrateLive": {
                        "host": host,
                        "block_migration": block_migration,
                        "disk_over_commit": disk_over_commit,
                        "force": force,
                        "ignore_az": ignore_az
                    }
                }
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
                payload=payload,
                migration_type=migration_type,
                vm_identifier=vm_identifier,
                host=host
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
