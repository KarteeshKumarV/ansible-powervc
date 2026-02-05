#!/usr/bin/python

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'PowerVC'}


DOCUMENTATION = '''
---
module: hmc_registration
author:
    - Karteesh Kumar Vipparapelli (@vkarteesh)
short_description: Register or unregister an HMC host in IBM PowerVC.
description:
  - Register or unregister a HMC managed host in IBM PowerVC.
options:
  name:
    description:
      - Display name of the HMC host.
    type: str
  access_ip:
    description:
      - Management IP address of the HMC host.
    type: str
  user:
    description:
      - User ID of the HMC host.
    type: str
  password:
    description:
      - Password for the HMC host user.
    required: true
    type: str
  host_id:
    description:
      - UUID of the HMC host.
    type: str
  state:
    description:
      - Desired state of the HMC host.
    required: true
    choices: [present, absent]
    type: str
'''

EXAMPLES = '''
  - name: Register an HMC host
    hosts: localhost
    gather_facts: no
    tasks:
       - name: Register the HMC host
         ibm.powervc.hmc_registration:
            cloud: "CLOUD"
            name: "HOST_DISPLAY_NAME"
            access_ip: "IP_ADDRESS"
            user: "USER_ID"
            password: "PASSWORD"
            state: present
         register: output
       - debug:
            var: output.result

  - name: Unregister an HMC host
    hosts: localhost
    gather_facts: no
    tasks:
       - name: Unregister the HMC host
         ibm.powervc.hmc_registration:
            cloud: "CLOUD"
            host_id: "HMC_UUID"
            state: absent
         register: output
       - debug:
            var: output.result

'''


from ansible_collections.openstack.cloud.plugins.module_utils.openstack import OpenStackModule
from ansible_collections.ibm.powervc.plugins.module_utils.crud_hmc_registration import host_ops


class HostAddModule(OpenStackModule):
    argument_spec = dict(
        host_id=dict(),
        user=dict(),
        access_ip=dict(),
        name=dict(),
        password=dict(no_log=True),
        state=dict(required=True, choices=['absent', 'present']),
    )
    module_kwargs = dict(
        supports_check_mode=True
    )

    def run(self):
        try:
            authtoken = self.conn.auth_token
            tenant_id = self.conn.session.get_project_id()
            host_id = self.params['host_id']
            user = self.params['user']
            name = self.params['name']
            access_ip = self.params['access_ip']
            password = self.params['password']
            state = self.params['state']
            if state == "absent":
                data = None
            elif state == "present":
                data = {
                    "hmc": {
                        "registration": {
                            "access_ip": access_ip,
                            "user_id": user,
                            "hmc_display_name": name,
                            "password": password,
                            "auto_add_certificate": True
                        }
                    }
                }
            res = host_ops(self, self.conn, authtoken, tenant_id, state, host_id, data)
            self.exit_json(changed=False, result=res)
        except Exception as e:
            self.fail_json(msg=f"An unexpected error occurred: {str(e)}", changed=False)


def main():
    module = HostAddModule()
    module()


if __name__ == '__main__':
    main()
