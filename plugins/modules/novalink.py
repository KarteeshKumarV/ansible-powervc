#!/usr/bin/python

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'PowerVC'}


DOCUMENTATION = '''
---
module: novalink
author:
    - Karteesh Kumar Vipparapelli (@vkarteesh)
short_description: Register or unregister a NovaLink host in IBM PowerVC.
description:
  - Register or unregister a NovaLink managed host in IBM PowerVC.
  - Update the Username password/ssh_key of the NovaLink Host
options:
  name:
    description:
      - Display name of the NovaLink host.
    type: str
  access_ip:
    description:
      - Management IP address of the NovaLink host.
    type: str
  user:
    description:
      - User ID of the NovaLink host.
    type: str
  password:
    description:
      - Password for the NovaLink host user.
    type: str
  ssh_key:
    description:
      - Private key for authentication.
    type: str
    no_log: true
  force:
    description:
      - Forcefully adds the NovaLink.
    type: bool
    default: False
  uninstall:
    description:
      - Removes the PowerVC software from the host.
    type: bool
    default: False
  stand_by:
    description:
      - Enables standby mode.
    type: bool
    default: False
  standby_tag:
    description:
      - Tag of the standby Host.
    choices: ["unplanned_maintenance","planned_maintenance","provisioning"]
    type: str
    default: "unplanned_maintenance"
  host_id:
    description:
      - HYPERVISOR_ID/MTMS of the NovaLink host.
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
         ibm.powervc.novalink:
            cloud: "CLOUD"
            name: "HOST_DISPLAY_NAME"
            access_ip: "IP_ADDRESS"
            user: "USER_ID"
            password: "PASSWORD"
            force: True
            state: present
         register: output
       - debug:
            var: output.result

  - name: Register a NovaLink host in standby mode
    hosts: localhost
    gather_facts: no
    tasks:
       - name: Register the NovaLink host
         ibm.powervc.novalink:
            cloud: "CLOUD"
            name: "HOST_DISPLAY_NAME"
            access_ip: "IP_ADDRESS"
            user: "USER_ID"
            password: "PASSWORD"
            stand_by: True
            standby_tag: "planned_maintenance"
            state: present
         register: output
       - debug:
            var: output.result

  - name: Register a NovaLink host using private key
    hosts: localhost
    gather_facts: no
    tasks:
       - name: Register the NovaLink host
         ibm.powervc.novalink:
            cloud: "CLOUD"
            name: "HOST_DISPLAY_NAME"
            host_type: "HOST_TYPE"
            access_ip: "IP_ADDRESS"
            user: "USER_ID"
            ssh_key: |
              -----BEGIN RSA PRIVATE KEY-----
              -------------------------------
              -----END RSA PRIVATE KEY-----
            state: present
         register: output
       - debug:
            var: output.result

  - name: Unregister a NovaLink host
    hosts: localhost
    gather_facts: no
    tasks:
       - name: Unregister the NovaLink host
         ibm.powervc.novalink:
            cloud: "CLOUD"
            host_id: "HYPERVISOR_ID/MTMS"
            state: absent
         register: output
       - debug:
            var: output.result

  - name: Removes the PowerVC software from the NovaLink host
    hosts: localhost
    gather_facts: no
    tasks:
       - name: Removes the PowerVC software from host
         ibm.powervc.novalink:
            cloud: "CLOUD"
            host_id: "HYPERVISOR_ID/MTMS"
            uninstall: True
            state: absent
         register: output
       - debug:
            var: output.result

  - name: Update the display name of the NovaLink host
    hosts: localhost
    gather_facts: no
    tasks:
        - name: Update NovaLink display name
          ibm.powervc.novalink:
            host_id: "HYPERVISOR_ID/MTMS"
            name: "UpdatedHost"
            state: present
         register: output
       - debug:
            var: output.result

  - name: Update the password of the NovaLink host
    hosts: localhost
    gather_facts: no
    tasks:
        - name: Update NovaLink password
          ibm.powervc.novalink:
            host_id: "HYPERVISOR_ID/MTMS"
            password: "newpassword"
            state: present
         register: output
       - debug:
            var: output.result

  - name: Update the sshkey of the NovaLink host
    hosts: localhost
    gather_facts: no
    tasks:
        - name: Update ssh_key
          ibm.powervc.novalink:
            host_id: "HYPERVISOR_ID/MTMS"
            access_ip: "9.2.4.5"
            user: "neo"
            ssh_key: |
              -----BEGIN RSA PRIVATE KEY-----
              -------------------------------
              -----END RSA PRIVATE KEY-----
            state: present
         register: output
       - debug:
            var: output.result

'''


from ansible_collections.openstack.cloud.plugins.module_utils.openstack import OpenStackModule
from ansible_collections.ibm.powervc.plugins.module_utils.crud_novalink import host_ops


class HostAddModule(OpenStackModule):
    argument_spec = dict(
        host_id=dict(type='str', required=False),
        user=dict(type='str', required=False),
        access_ip=dict(type='str', required=False),
        name=dict(type='str'),
        host_group=dict(default="Default Group", choices=["Default Group", "Default Reservation Group"], required=False),
        password=dict(type='str', no_log=True),
        stand_by=dict(type='bool', default=False),
        uninstall=dict(type='bool', default=False),
        ssh_key=dict(type="str", no_log=True),
        standby_tag=dict(default="unplanned_maintenance", choices=["unplanned_maintenance", "planned_maintenance", "provisioning"], required=False),
        state=dict(choices=['absent', 'present'], default='present'),
        force=dict(type='bool', default=False),
    )
    module_kwargs = dict(
        supports_check_mode=False
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
            private_key_data = self.params['ssh_key']
            stand_by = self.params['stand_by']
            standby_tag = self.params['standby_tag']
            force = self.params['force']
            uninstall = self.params['uninstall']
            state = self.params['state']
            host_group = self.params['host_group']
            if host_group == "Default Reservation Group":
                host_group = "-".join(host_group.split())

            if state == "absent" and not host_id:
                self.fail_json(
                    msg="host_id must be provided when state is 'absent'",
                    changed=False
                )

            data = None
            if state == "absent" and uninstall:
                data = "uninstall_novalink"

            if state == "present" and not host_id:
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
            elif state == "present" and host_id:
                registration = {}
                if access_ip:
                    registration["access_ip"] = access_ip
                if user:
                    registration["user_id"] = user
                if name:
                    registration["host_display_name"] = name
                if password:
                    registration["password"] = password
                if private_key_data:
                    registration["private_key_data"] = private_key_data
                registration["auto_add_host_key"] = True
                registration["force_switch"] = force
                data = {
                    "registration": registration
                }
            res = host_ops(self, self.conn, authtoken, tenant_id, state, host_id, data)
            self.exit_json(**res)
        except Exception as e:
            self.fail_json(msg=f"An unexpected error occurred: {str(e)}", changed=False)


def main():
    module = HostAddModule()
    module()


if __name__ == '__main__':
    main()
