#!/usr/bin/python

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'PowerVC'}


DOCUMENTATION = '''
---
module: all_volumes
author:
    - Karteesh Kumar Vipparapelli (@vkarteesh)
short_description: Fetches the Details of all the volumes
description:
  - This playbook helps in performing the Get operation on the All the Volumes.
options:
  host_metadata_name:
    description:
      - Host Name from the Storage specific metadata
    required: true
    type: str

'''

EXAMPLES = '''
  - name: All Volume Details Playbook
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
       - name: Perform Volume Details Operation
         ibm.powervc.all_volumes:
            auth: "{{ auth }}"
            host_metadata_name: "HOST_METADATA_NAME"
            validate_certs: no
         register: result
       - debug:
            var: result

  - name: All Volume Details Playbook
    hosts: localhost
    gather_facts: no
    tasks:
       - name: Perform Volume Details Operation
         ibm.powervc.all_volumes:
            cloud: "CLOUD_NAME"
            host_metadata_name: "HOST_METADATA_NAME"
            validate_certs: no
         register: result
       - debug:
            var: result
'''


from ansible_collections.openstack.cloud.plugins.module_utils.openstack import OpenStackModule
from ansible_collections.ibm.powervc.plugins.module_utils.crud_all_volumes import volume_ops


class AllVolumeInfoModule(OpenStackModule):
    argument_spec = dict(
        host_metadata_name=dict(required=True),
    )
    module_kwargs = dict(
        supports_check_mode=True
    )

    def run(self):
        authtoken = self.conn.auth_token
        tenant_id = self.conn.session.get_project_id()
        host = self.params['host_metadata_name']
        try:
            res = volume_ops(self, self.conn, authtoken, tenant_id, host)
            self.exit_json(changed=True, result=res)
        except Exception as e:
            self.fail_json(msg=f"An unexpected error occurred: {str(e)}", changed=True)


def main():
    module = AllVolumeInfoModule()
    module()


if __name__ == '__main__':
    main()
