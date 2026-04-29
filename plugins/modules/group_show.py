#!/usr/bin/python


DOCUMENTATION = r'''
---
module: group_show
short_description: Show live backend information of a consistency group


description:
  - Retrieves live information about a remote copy consistency group
    from the Storwize backend.
  - This uses the C(group-show) action API.
  - The operation is read-only and does not modify any resources.

author:
    - Karteesh Kumar Vipparapelli (@vkarteesh)

options:
  id:
    description:
      - ID of the consistency group.
    required: true
    type: str

  secondary:
    description:
      - If set to C(true), retrieves information from the secondary backend.
      - Default is C(false).
    required: false
    type: bool
    default: false

extends_documentation_fragment:
  - openstack.cloud.openstack

notes:
  - This module performs a POST action but is read-only.
  - The module always returns C(changed=false).

requirements:
  - "python >= 3.6"
  - "openstacksdk"
'''

EXAMPLES = r'''
- name: Show primary backend information
  ibm.powervc.group_show:
    id: 123456

- name: Show secondary backend information
  ibm.powervc.group_show:
    id: 123456
    secondary: true
'''


from ansible_collections.openstack.cloud.plugins.module_utils.openstack import (
    OpenStackModule
)

from ansible_collections.ibm.powervc.plugins.module_utils.crud_group_show import (
    group_show_ops
)


class GroupShowModule(OpenStackModule):

    argument_spec = dict(
        id=dict(type='str', required=True),
        secondary=dict(type='bool', default=False)
    )

    module_kwargs = dict(
        supports_check_mode=True
    )

    def run(self):

        authtoken = self.conn.auth_token
        tenant_id = self.conn.session.get_project_id()

        group_id = self.params.get("id")
        secondary = self.params.get("secondary")

        # Validate group exists in OpenStack
        existing_group = self.conn.block_storage.get_group(group_id)

        if not existing_group:
            self.fail_json(
                msg=f"Consistency group with id '{group_id}' not found",
                changed=False
            )

        if self.check_mode:
            self.exit_json(
                changed=False,
                msg="Group show operation would be executed"
            )

        result = group_show_ops(
            mod=self,
            connectn=self.conn,
            authtoken=authtoken,
            tenant_id=tenant_id,
            group_id=group_id,
            secondary=secondary
        )

        self.exit_json(
            changed=False,
            result=result
        )


def main():
    module = GroupShowModule()
    module()


if __name__ == "__main__":
    main()