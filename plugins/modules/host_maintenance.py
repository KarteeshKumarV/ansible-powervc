#!/usr/bin/python

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'PowerVC'}


DOCUMENTATION = '''
---
module: host_maintenance
author:
    - Karteesh Kumar Vipparapelli (@vkarteesh)
short_description: Enable or disable host maintenance mode and migrate virtual machines in IBM PowerVC
description:
  - Enable or disable maintenance mode for a PowerVC host.
  - Supports migration of virtual machines based on placement policy.
options:
  host:
    description:
      - ID of the Host
    required: true
    type: str
  status:
    description:
      - Desired maintenance status of the host.
    required: true
    choices: ['enable', 'disable']
    type: str
  migrate:
    description:
      - VM migration behavior during maintenance.
    choices: ['all', 'active_only']
    type: str
  target_host:
    description:
      - ID of the destination host
    type: str

'''

EXAMPLES = '''
  - name: Enable Host Manintenance Playbook
    hosts: localhost
    gather_facts: no
    tasks:
       - name: Enable Maintenance mode
         ibm.powervc.host_maintenance:
            cloud: "CLOUD"
            host: "HOST_ID"
            status: "enable"
         register: output
       - debug:
            var: output.result

  - name: Enable Host Manintenance and migrate All VMs based on Placement Policy
    hosts: localhost
    gather_facts: no
    tasks:
       - name: Enable maintenance mode and migrate all VMs
         ibm.powervc.host_maintenance:
            cloud: "CLOUD"
            host: "HOST_ID"
            status: "enable"
            migrate: "all"
         register: result
       - debug:
            var: result

  - name: Enable Host Manintenance and migrate Only Active VMs based on Placement Policy
    hosts: localhost
    gather_facts: no
    tasks:
       - name: Enable maintenance mode and migrate only active VMs
         ibm.powervc.host_maintenance:
            cloud: "CLOUD"
            host: "HOST_ID"
            status: "enable"
            migrate: "active_only"
         register: output
       - debug:
            var: output.result

  - name: Disable Host maintenance
    hosts: localhost
    gather_facts: no
    tasks:
       - name: Disable the host maintenance mode
         ibm.powervc.host_maintenance:
            cloud: "CLOUD"
            host: "HOST_ID"
            status: "disable"
         register: output
       - debug:
            var: output.result

'''


from ansible_collections.openstack.cloud.plugins.module_utils.openstack import OpenStackModule
from ansible_collections.ibm.powervc.plugins.module_utils.crud_maintenance import maintenance_ops


class HostMaintenanceModule(OpenStackModule):
    argument_spec = dict(
        host=dict(required=True),
        status=dict(required=True),
        migrate=dict(choices=['all', 'active_only']),
        target_host=dict(),
    )
    module_kwargs = dict(
        supports_check_mode=True,
    )

    def run(self):
        authtoken = self.conn.auth_token
        tenant_id = self.conn.session.get_project_id()
        host = self.params['host']
        status = self.params['status']
        migrate = self.params['migrate']
        target_host = self.params['target_host']
        try:
            res = maintenance_ops(self, self.conn, authtoken, tenant_id, host, status, migrate, target_host)
            self.exit_json(changed=True, result=res)
        except Exception as e:
            self.fail_json(msg=f"An unexpected error occurred: {str(e)}", changed=True)


def main():
    module = HostMaintenanceModule()
    module()


if __name__ == '__main__':
    main()
