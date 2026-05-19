#!/usr/bin/python

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'PowerVC'
}

DOCUMENTATION = '''
---
module: server
short_description: Create/Delete/Update PowerVC Virtual Machines
description:
  - Create VM
  - Delete VM
  - Assign/Unassign Virtual Serial Number (VSN)
options:
  name:
    description:
      - Name of the VM
    type: str
  id:
    description:
      - ID of the VM
    type: str
  flavor:
    description:
      - Flavor name
    type: str
  image:
    description:
      - Image name
    type: str
  host:
    description:
      - Host name
    type: str
  collocation_rule_name:
    description:
      - Collocation rule name
    type: str
  max_count:
    description:
      - Maximum VM count
    type: int
  scg_id:
    description:
      - Storage Connectivity Group ID
    type: str
  key_name:
    description:
      - SSH key name
    type: str
  user_data:
    description:
      - Cloud-init/userdata
    type: str
  virtual_serial_number:
    description:
      - Virtual Serial Number
      - auto
      - none
      - ABCD007
    type: str
  nics:
    description:
      - VM networks
    type: list
    elements: raw
    default: []
  image_volume_override:
    description:
      - Volume/template mapping
    type: list
    elements: raw
    default: []
  volume_name:
    description:
      - Volume names
    type: list
    elements: raw
    default: []
  volume_id:
    description:
      - Volume IDs
    type: list
    elements: str
    default: []
  state:
    description:
      - Desired state
    choices: [present, absent]
    required: true
    type: str
'''

EXAMPLES = '''

  - name: PowerVC Create VM Playbook
    hosts: localhost
    gather_facts: no
    vars:
      auth:
        auth_url: https://<POWERVC>:5000/v3
        project_name: PROJECT_NAME
        username: USERID
        password: PASSWORD
        project_domain_name: Default
        user_domain_name: Default

    tasks:

      - name: Create VM
        ibm.powervc.server:
          auth: "{{ auth }}"
          name: "VM_NAME"
          image: "IMAGE_NAME"
          flavor: "FLAVOR_NAME"
          host: "HOST_NAME"

          nics:
            - network_name: "NETWORK_NAME"
              fixed_ip: "192.168.10.20"

          volume_name:
            - "volume1"
            - "volume2"

          state: present

          validate_certs: false

        register: result

      - debug:
          var: result


  - name: PowerVC Create VM using cloud entry
    hosts: localhost
    gather_facts: no

    tasks:

      - name: Create VM using clouds.yaml
        ibm.powervc.server:
          cloud: "powervc"

          name: "VM_NAME"

          image: "IMAGE_NAME"

          flavor: "FLAVOR_NAME"

          host: "HOST_NAME"

          user_data: |
            #!/bin/bash
            yum update -y

          nics:
            - network_name: "NETWORK_NAME"

          state: present

          validate_certs: false

        register: result

      - debug:
          var: result


  - name: PowerVC Create VM with SCG
    hosts: localhost
    gather_facts: no

    tasks:

      - name: Create VM with Storage Connectivity Group
        ibm.powervc.server:
          cloud: "powervc"

          name: "VM_NAME"

          image: "IMAGE_NAME"

          flavor: "FLAVOR_NAME"

          host: "HOST_NAME"

          scg_id: "SCG_ID"

          nics:
            - network_name: "NETWORK_NAME"

          state: present

          validate_certs: false

        register: result

      - debug:
          var: result


  - name: PowerVC Create VM with image volume override
    hosts: localhost
    gather_facts: no

    tasks:

      - name: Create VM with image volume override
        ibm.powervc.server:
          cloud: "powervc"

          name: "VM_NAME"

          image: "IMAGE_NAME"

          flavor: "FLAVOR_NAME"

          host: "HOST_NAME"

          image_volume_override:
            - volume_id: "VOLUME_ID"
              template_id: "TEMPLATE_ID"

          nics:
            - network_name: "NETWORK_NAME"

          state: present

          validate_certs: false

        register: result

      - debug:
          var: result


  - name: PowerVC Delete VM
    hosts: localhost
    gather_facts: no

    tasks:

      - name: Delete VM
        ibm.powervc.server:
          cloud: "powervc"

          name: "VM_NAME"

          state: absent

          validate_certs: false

        register: result

      - debug:
          var: result


  - name: Create VM with auto generated VSN
    hosts: localhost
    gather_facts: no

    tasks:

      - name: Create VM with auto VSN
        ibm.powervc.server:
          cloud: "powervc"

          name: "vsn_auto_vm"

          image: "IMAGE_NAME"

          flavor: "FLAVOR_NAME"

          host: "HOST_NAME"

          virtual_serial_number: "auto"

          nics:
            - network_name: "NETWORK_NAME"

          state: present

          validate_certs: false

        register: result

      - debug:
          var: result


  - name: Create VM with custom VSN
    hosts: localhost
    gather_facts: no

    tasks:

      - name: Create VM using custom VSN
        ibm.powervc.server:
          cloud: "powervc"

          name: "vsn_custom_vm"

          image: "IMAGE_NAME"

          flavor: "FLAVOR_NAME"

          host: "HOST_NAME"

          virtual_serial_number: "ABCD007"

          nics:
            - network_name: "NETWORK_NAME"

          state: present

          validate_certs: false

        register: result

      - debug:
          var: result


  - name: Assign auto VSN to existing VM
    hosts: localhost
    gather_facts: no

    tasks:

      - name: Assign auto VSN
        ibm.powervc.server:
          cloud: "powervc"

          name: "existing_vm"

          virtual_serial_number: "auto"

          state: present

          validate_certs: false

        register: result

      - debug:
          var: result


  - name: Assign custom VSN to existing VM
    hosts: localhost
    gather_facts: no

    tasks:

      - name: Assign custom VSN
        ibm.powervc.server:
          cloud: "powervc"

          name: "existing_vm"

          virtual_serial_number: "ABCD007"

          state: present

          validate_certs: false

        register: result

      - debug:
          var: result


  - name: Unassign VSN from existing VM
    hosts: localhost
    gather_facts: no

    tasks:

      - name: Unassign VSN
        ibm.powervc.server:
          cloud: "powervc"

          name: "existing_vm"

          virtual_serial_number: "none"

          state: present

          validate_certs: false

        register: result

      - debug:
          var: result

'''

from ansible_collections.openstack.cloud.plugins.module_utils.openstack import OpenStackModule

from ansible_collections.ibm.powervc.plugins.module_utils.crud_server import (
    server_ops,
    server_flavor,
    get_collocation_rules_id
)

import copy
import base64


class ServerOpsModule(OpenStackModule):
    argument_spec = dict(
        name=dict(required=False),
        id=dict(required=False),
        volume_id=dict(
            default=[],
            type='list',
            elements='str'
        ),
        volume_name=dict(
            default=[],
            type='list',
            elements='str'
        ),
        flavor=dict(),
        image=dict(),
        key_name=dict(),
        host=dict(),
        metadata=dict(
            type='raw',
            aliases=['meta']
        ),
        nics=dict(
            default=[],
            type='list',
            elements='raw'
        ),
        image_volume_override=dict(
            default=[],
            type='list',
            elements='raw'
        ),
        network=dict(),
        user_data=dict(),
        virtual_serial_number=dict(type='str'),
        max_count=dict(type='int'),
        collocation_rule_name=dict(),
        scg_id=dict(),
        security_groups=dict(
            default=[],
            type='list',
            elements='str'
        ),
        state=dict(
            choices=['present', 'absent']
        ),
    )
    module_kwargs = dict(
        supports_check_mode=True
    )

    def _parse_nics(self):
        nics = []
        stringified_nets = self.params['nics']
        if not isinstance(stringified_nets, list):
            self.fail_json(
                msg="The 'nics' parameter must be a list."
            )
        nets = [
            (
                dict((nested_net.split('='),))
                for nested_net in net.split(',')
            )
            if isinstance(net, str) else net
            for net in stringified_nets
        ]
        for net in nets:
            if not isinstance(net, dict):
                self.fail_json(
                    msg="Each entry in the 'nics' parameter must be a dict."
                )
            if net.get('network_id'):
                nics.append({
                    "uuid": net["network_id"]
                })
            elif net.get('network_name'):
                network_id = self.conn.network.find_network(
                    net['network_name'],
                    ignore_missing=False
                ).id
                net = copy.deepcopy(net)
                del net['network_name']
                net['uuid'] = network_id
                nics.append(net)
            elif net.get('fixed_ip'):
                nics.append(net)
            elif net.get('port_id'):
                nics.append({
                    "port": net["port_id"]
                })
            elif net.get('port_name'):
                port_id = self.conn.network.find_port(
                    net['port_name'],
                    ignore_missing=False
                ).id
                net = copy.deepcopy(net)
                del net['port_name']
                net['port'] = port_id
                nics.append(net)
            if 'tag' in net:
                nics[-1]['tag'] = net['tag']
        return nics

    def _parse_image_volume_override(self):
        image_volume_override = []
        stringified_nets = self.params['image_volume_override']
        if not isinstance(stringified_nets, list):
            self.fail_json(
                msg="The 'image_volume_override' parameter must be a list."
            )
        nets = [
            (
                dict((nested_net.split('='),))
                for nested_net in net.split(',')
            )
            if isinstance(net, str) else net
            for net in stringified_nets
        ]
        for net in nets:
            if not isinstance(net, dict):
                self.fail_json(
                    msg="Each entry in image_volume_override must be dict."
                )
            if net.get('volume_id'):
                image_volume_override.append(net)
            elif net.get('template_id'):
                image_volume_override.append(net)
        return image_volume_override

    def run(self):
        try:
            authtoken = self.conn.auth_token
            vm_name = self.params['name']
            vmid = self.params['id']
            state = self.params['state']
            image = self.params['image']
            max_count = self.params['max_count']
            availability_zone = self.params['host']
            flavor = self.params['flavor']
            collocation_rule = self.params['collocation_rule_name']
            nics = self.params['nics']
            image_vol_template = self.params['image_volume_override']
            key_name = self.params['key_name']
            volume_name = self.params['volume_name']
            volume_id = self.params['volume_id']
            scg_id = self.params['scg_id']
            user_data = self.params['user_data']
            virtual_serial_number = self.params['virtual_serial_number']
            tenant_id = self.conn.session.get_project_id()
            server = self.conn.compute.find_server(
                vm_name,
                ignore_missing=True
            )
            #
            # PRESENT
            #
            if state == "present":
                #
                # UPDATE EXISTING VM VSN
                #
                if server and virtual_serial_number is not None:
                    if virtual_serial_number == "none":
                        vm_data = {
                            "unassign_vsn": None
                        }
                    else:
                        vm_data = {
                            "assign_vsn": {
                                "virtual_serial_number":
                                    virtual_serial_number
                            }
                        }
                    res = server_ops(
                        self,
                        self.conn,
                        authtoken,
                        tenant_id,
                        vm_name,
                        "vsn_update",
                        vm_data,
                        vm_id=server.id
                    )

                #
                # CREATE VM
                #
                else:
                    flavor_id = self.conn.compute.find_flavor(
                        flavor,
                        ignore_missing=False
                    ).id

                    imageRef = self.conn.compute.find_image(
                        image,
                        ignore_missing=False
                    ).id
                    nics = self._parse_nics()
                    if user_data:
                        base64_encoded = base64.b64encode(
                            user_data.encode('utf-8')
                        )
                        userdata = base64_encoded.decode('utf-8')
                    else:
                        userdata = None
                    if not volume_id:
                        vol_id = []
                        for name in volume_name:
                            vol_id.append(
                                self.conn.block_storage.find_volume(
                                    name,
                                    ignore_missing=False
                                ).id
                            )
                        vol_list = []
                        index = 1
                        for uuid in vol_id:
                            entry = {
                                "boot_index": index,
                                "delete_on_termination": False,
                                "destination_type": "volume",
                                "source_type": "volume",
                                "uuid": uuid
                            }
                            vol_list.append(entry)
                            index += 1
                    else:
                        vol_list = []
                        index = 1
                        for uuid in volume_id:
                            entry = {
                                "boot_index": index,
                                "delete_on_termination": False,
                                "destination_type": "volume",
                                "source_type": "volume",
                                "uuid": uuid
                            }
                            vol_list.append(entry)
                            index += 1
                    volid = None
                    template_id = None
                    if image_vol_template:
                        volid = image_vol_template[0].get(
                            'volume_id',
                            None
                        )

                        template_id = image_vol_template[0].get(
                            'template_id',
                            None
                        )
                    flavor = server_flavor(
                        self,
                        self.conn,
                        authtoken,
                        tenant_id,
                        flavor_id,
                        imageRef,
                        volid,
                        template_id,
                        scg_id,
                        virtual_serial_number
                    )
                    collocation_rule_id = get_collocation_rules_id(
                        self,
                        self.conn,
                        authtoken,
                        tenant_id,
                        collocation_rule
                    )
                    if availability_zone:
                        availability_zone = ":" + availability_zone
                    vm_data = {
                        "server": {
                            "name": vm_name,
                            "imageRef": imageRef,
                            "key_name": key_name,
                            "availability_zone": availability_zone,
                            "block_device_mapping_v2": vol_list,
                            "max_count": max_count,
                            "config_drive": True,
                            "user_data": userdata,
                            "networks": nics,
                            "powervm:virtual_serial_number":
                                virtual_serial_number,
                            "flavor": flavor
                        },
                        "os:scheduler_hints": collocation_rule_id
                    }

                    res = server_ops(
                        self,
                        self.conn,
                        authtoken,
                        tenant_id,
                        vm_name,
                        "present",
                        vm_data,
                        vm_id=None
                    )

            #
            # ABSENT
            #

            elif state == "absent":
                res = server_ops(
                    self,
                    self.conn,
                    authtoken,
                    tenant_id,
                    vm_name,
                    "absent",
                    None,
                    vm_id=vmid
                )
            self.exit_json(
                changed=True,
                result=res
            )
        except Exception as e:
            self.fail_json(
                msg=f"An unexpected error occurred: {str(e)}",
                changed=False
            )


def main():
    module = ServerOpsModule()
    module()


if __name__ == '__main__':
    main()