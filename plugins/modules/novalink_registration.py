#!/usr/bin/python

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'PowerVC'}


DOCUMENTATION = '''
---
module: novalink_registration
author:
    - Karteesh Kumar Vipparapelli (@vkarteesh)
short_description: Register or unregister a NovaLink host in IBM PowerVC.
description:
  - Register or unregister a NovaLink managed host in IBM PowerVC.
options:
  host_display_name:
    description:
      - Display name of the NovaLink host.
    required: true
    type: str
  host_type:
    description:
      - Type of the host being registered.
    required: true
    choices: [powervm]
	type: str
  access_ip:
    description:
      - Management IP address of the NovaLink host.
    required: true
    type: str
  user_id:
    description:
      - User ID of the NovaLink host.
    required: true
    type: str
  password:
    description:
      - Password for the NovaLink host user.
    required: true
    type: str
  state:
    description:
      - Desired state of the NovaLink host.
    required: true
    choices: [present, absent]
    type: str
'''

EXAMPLES = '''
  - name: Register a NovaLink host
    hosts: localhost
    gather_facts: no
    tasks:
       - name: Register the NovaLink host
         ibm.powervc.novalink_registration:
            cloud: "CLOUD"
            host_display_name: "HOST_DISPLAY_NAME"
            host_type: "HOST_TYPE"
            access_ip: "IP_ADDRESS"
            user_id: "USER_ID"
            password: "PASSWORD"
            state: present
            validate_certs: no
         register: result
       - debug:
            var: result

  - name: Unregister a NovaLink host
    hosts: localhost
    gather_facts: no
    tasks:
       - name: Unregister the NovaLink host
         ibm.powervc.novalink_registration:
            cloud: "CLOUD"
            host_display_name: "HOST_DISPLAY_NAME"
            state: absent
            validate_certs: no
         register: result
       - debug:
            var: result

'''


from ansible_collections.openstack.cloud.plugins.module_utils.openstack import OpenStackModule
from ansible_collections.ibm.powervc.plugins.module_utils.crud_novalink_registration import host_ops


class HostAddModule(OpenStackModule):
    argument_spec = dict(
        host_id=dict(required=False),
        user_id=dict(required=False),
        access_ip=dict(required=False),
        host_display_name=dict(),
        password=dict(type='str', no_log=True),
        host_type=dict(),
        state=dict(choices=['absent', 'present']),
    )
    module_kwargs = dict(
        supports_check_mode=True
    )

    def run(self):
        try:
            authtoken = self.conn.auth_token
            tenant_id = self.conn.session.get_project_id()
            host_id = self.params['host_id']
            user_id = self.params['user_id']
            host_display_name = self.params['host_display_name']
            host_type = self.params['host_type']
            access_ip = self.params['access_ip']
            password = self.params['password']
            state = self.params['state']
            if state == "absent":
                data = None
            elif state == "present":
                data = {
                    "host": {
                        "registration": {
                            "access_ip": access_ip,
                            "user_id": user_id,
                            "host_type": host_type,
                            "asynchronous": True,
                            "host_standby": False,
                            "host_group": "Default Group",
                            "host_display_name": host_display_name,
                            "password": password,
                            "force_unmanage": False,
                            "auto_add_host_key": True,
                            "force_switch": False
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
