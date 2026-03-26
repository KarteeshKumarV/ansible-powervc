#!/usr/bin/python
DOCUMENTATION = r'''
---
module: fabric
short_description: Manage SAN fabrics in PowerVC
description:
  - Register, delete, update or retrieve SAN fabrics in PowerVC.
options:
  state:
    description:
      - Desired state of the fabric.
    type: str
    choices: [present, absent]
    default: present
  id:
    description:
      - ID of the SAN fabric.
    type: str
  host:
    description:
      - IP address or the host name that is used to connect to the switch.
    type: str
  user:
    description:
      - Username for connecting to the switch.
    type: str
  password:
    description:
      - Password for connecting to the switch.
    type: str
    no_log: true
  name:
    description:
      - Display name of the fabric.
    type: str
  type:
    description:
      - Type of fabric.
    type: str
    choices: [brocade, cisco, generic]
  zoning_policy:
    description:
      - Zoning policy.
    type: str
    choices: [initiator-target, initiator, initiator-vfc]
  auto_add_host_key:
    description:
      - Automatically add host key.
    type: bool
    default: True
  virtual_fabric_id:
    description:
      - Virtual Fabric ID used to connect to a Brocade switch.
    type: str
  port:
    description:
      - SSH port used to connect to a Cisco switch.
    type: str
    default: 22
  vsan:
    description:
      - virtual SAN for Cisco switches only.
    type: str
'''

EXAMPLES = r'''
# Get all fabrics
- name: Get fabrics
  ibm.powervc.fabric:
    cloud: powervc

# Get specific fabric
- name: Get fabric
  ibm.powervc.fabric:
    cloud: powervc
    id: fab123

# Register fabric
- name: Register fabric
  ibm.powervc.fabric:
    cloud: powervc
    state: present
    host: 9.2.4.6
    user: admin
    password: password
    name: Fabric1
    type: brocade
    zoning_policy: initiator

# Delete fabric
- name: Delete fabric
  ibm.powervc.fabric:
    cloud: powervc
    state: absent
    id: fab123

# Update fabric name
- name: Update fabric
  ibm.powervc.fabric:
    cloud: powervc
    state: absent
    id: fab123
    name: Fabric12
'''


from ansible_collections.ibm.powervc.plugins.module_utils.crud_fabric import (
    fabric_ops,
    get_endpoint_url_by_service_name,
)
from ansible_collections.openstack.cloud.plugins.module_utils.openstack import (
    OpenStackModule,
)


class FabricModule(OpenStackModule):
    argument_spec = dict(
        state=dict(type="str", choices=["present", "absent"], default="present"),
        id=dict(type="str"),
        host=dict(type="str"),
        user=dict(type="str"),
        password=dict(type="str", no_log=True),
        ssh_key=dict(type="str", no_log=True),
        name=dict(type="str"),
        type=dict(type="str", choices=["brocade", "cisco", "generic"]),
        zoning_policy=dict(type="str", choices=["initiator-target", "initiator","initiator-vfc"]),
        auto_add_host_key=dict(type="bool", default=True),
        virtual_fabric_id=dict(type="str"),
        port=dict(type="str", default="22"),
        vsan=dict(type="str"),
        restart=dict(type="bool"),
    )
    module_kwargs = dict(supports_check_mode=True)


    def run(self):
        authtoken = self.conn.auth_token
        tenant_id = self.conn.session.get_project_id()
        verify = self.conn.session.verify
        state = self.params.get("state")
        fabric_id = self.params.get("id")
        host = self.params.get("host")
        user = self.params.get("user")
        password = self.params.get("password")
        private_key_data = self.params.get("ssh_key")
        name = self.params.get("name")
        type = self.params.get("type")
        zoning_policy = self.params.get("zoning_policy")
        auto_add_host_key = self.params.get("auto_add_host_key")
        virtual_fabric_id = self.params.get("virtual_fabric_id")
        port = self.params.get("port")
        vsan = self.params.get("vsan")
        restart = self.params.get("restart")
        endpoint = get_endpoint_url_by_service_name(
            self, self.conn, "volume", tenant_id
        )
        body = None
        if state == "present" and not fabric_id and host:
            if type == "cisco" and not vsan:
                self.fail_json(
                    msg="For 'cisco' fabric type, 'vsan' and 'port' are mandatory. Parameter 'port' defaults to 22 if not specified."
                )
            registration = {
                "access_ip": host,
                "user_id": user,
                "password": password,
                "fabric_display_name": name,
                "fabric_type": type,
                "zoning_policy": zoning_policy,
                "auto_add_host_key": auto_add_host_key,
            }
            if type == "brocade":
                registration["virtual_fabric_id"] = virtual_fabric_id
            if type == "cisco":
                registration["port"] = port
                registration["vsan"] = vsan
            body = {
                "fabric": {
                    "registration": registration
                }
            }
        elif state == "present" and fabric_id:
            update_fields = {}
            if host:
                update_fields["access_ip"] = host
            if user:
                update_fields["user_id"] = user
            if password:
                update_fields["password"] = password
            if private_key_data:
                update_fields["private_key_data"] = private_key_data
            if name:
                update_fields["fabric_display_name"] = name
            if restart:
                update_fields["restart"] = restart
            if update_fields:
                body = {
                        "registration": update_fields
                    }
        result = fabric_ops(
            module=self,
            endpoint=endpoint,
            authtoken=authtoken,
            tenant_id=tenant_id,
            verify=verify,
            state=state,
            fabric_id=fabric_id,
            body=body,
        )
        self.exit_json(**result)


def main():
    module = FabricModule()
    module()


if __name__ == "__main__":
    main()
