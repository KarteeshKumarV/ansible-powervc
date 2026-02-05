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
        user=dict(required=False),
        access_ip=dict(required=False),
        name=dict(),
        host_group=dict(default="Default Group", choices=["Default Group","Default-Reservation-Group"], required=False),
        password=dict(type='str', no_log=True),
        stand_by=dict(type='bool', default=False),
        private_key_data=dict(no_log=True),
        standby_tag=dict(default="unplanned_maintenance", choices=["unplanned_maintenance","planned_maintenance","provisioning"], required=False),
        state=dict(choices=['absent', 'present'], required=True),
        force=dict(type='bool', default=False),
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
            private_key_data = self.params['private_key_data']
            host_group = self.params['host_group']
            stand_by = self.params['stand_by']
            standby_tag = self.params['standby_tag']
            force = self.params['force']
            state = self.params['state']

            if state == "absent" and not host_id:
                self.fail_json(
                    msg="host_id must be provided when state is 'absent'",
                    changed=False
                )

            data = None
            if state == "present":
                registration = {
                          "access_ip": access_ip,
                          "user_id": user,
                          "host_type": "powervm",
                          "asynchronous": True,
                          "host_standby": stand_by,
                          "host_group": host_group,
                          "host_display_name": name,
                          "password": password,
                          "private_key_data": private_key_data,
                          "force_unmanage": False,
                          "auto_add_host_key": True,
                          "force_switch": force
                                 }
                if stand_by:
                    registration["standby_tag"] = standby_tag
                    data = {
                        "host": {
                            "registration": registration
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
