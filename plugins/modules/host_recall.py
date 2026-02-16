#!/usr/bin/python

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'PowerVC'}


DOCUMENTATION = '''
---
module: host_recall
author:
    - Karteesh Kumar Vipparapelli (@vkarteesh)
short_description: Recall virtual machines back to a PowerVC host
description:
  - Recall virtual machines back to a specified PowerVC compute host.
  - Used after host maintenance to restore virtual machines to their original host.
options:
  host:
    description:
      - HYPERVISOR_ID/MTMS of the compute host to recall virtual machines.
    required: true
    type: str

'''

EXAMPLES = '''
  - name: Recall virtual machines back to a PowerVC host
    hosts: localhost
    gather_facts: no
    tasks:
       - name: Recall virtual machines to the specified host
         ibm.powervc.host_recall:
            cloud: "CLOUD"
            host: "HOST_ID"
         register: result
       - debug:
            var: result

  - name: Recall virtual machines back to a PowerVC host
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
       - name: Recall virtual machines to the specified host
         ibm.powervc.host_recall:
            auth: "{{ auth }}"
            host: "HOST_ID"
         register: result
       - debug:
            var: result
'''


from ansible_collections.openstack.cloud.plugins.module_utils.openstack import OpenStackModule
from ansible_collections.ibm.powervc.plugins.module_utils.crud_recall import recall_ops


class HostRecallModule(OpenStackModule):
    argument_spec = dict(
        host=dict(required=True)
    )
    module_kwargs = dict(
        supports_check_mode=False,
    )

    def run(self):
        authtoken = self.conn.auth_token
        tenant_id = self.conn.session.get_project_id()
        host = self.params['host']
        try:
            res = recall_ops(self, self.conn, authtoken, tenant_id, host)
            self.exit_json(changed=True, result=res)
        except Exception as e:
            self.fail_json(msg=f"An unexpected error occurred: {str(e)}", changed=True)


def main():
    module = HostRecallModule()
    module()


if __name__ == '__main__':
    main()
