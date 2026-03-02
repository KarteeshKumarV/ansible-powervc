#!/usr/bin/python

DOCUMENTATION = r'''
---
module: group_action

short_description: Perform action operations on a consistency group

description:
  - Perform show, relationship, start, and stop operations
    on the consistency group.

author:
    - Karteesh Kumar Vipparapelli (@vkarteesh)

options:
  id:
    description:
      - ID of the consistency group.
    required: true
    type: str

  action:
    description:
      - Action to perform.
    required: true
    type: str
    choices:
      - show
      - relationship
      - start
      - stop

  secondary:
    description:
      - Target secondary site.
    type: bool
    default: false

  primary:
    description:
      - Primary role during start action.
    type: str
    choices:
      - master
      - aux

  access:
    description:
      - Enable access during stop action.
    type: bool
    default: false
'''

from ansible_collections.openstack.cloud.plugins.module_utils.openstack import (
    OpenStackModule
)

from ansible_collections.ibm.powervc.plugins.module_utils.crud_group_action import (
    group_action
)


class GroupActionModule(OpenStackModule):

    argument_spec = dict(
        id=dict(type='str', required=True),
        action=dict(
            type='str',
            required=True,
            choices=['show', 'relationship', 'start', 'stop']
        ),
        secondary=dict(type='bool', default=False),
        primary=dict(type='str', choices=['master', 'aux']),
        access=dict(type='bool', default=False)
    )

    module_kwargs = dict(
        supports_check_mode=True
    )

    def run(self):

        authtoken = self.conn.auth_token
        tenant_id = self.conn.session.get_project_id()

        group_id = self.params["id"]
        action = self.params["action"]
        secondary = self.params["secondary"]
        primary = self.params.get("primary")
        access = self.params["access"]

        # Validate group existence
        if not self.conn.block_storage.get_group(group_id):
            self.fail_json(
                msg=f"Consistency group '{group_id}' not found",
                changed=False
            )

        # Additional validations
        if action == "start" and not primary:
            self.fail_json(
                msg="Parameter 'primary' is required for start action",
                changed=False
            )

        if action in ["show", "relationship"] and primary:
            self.fail_json(
                msg="'primary' parameter is only valid for start action",
                changed=False
            )

        if action != "stop" and access:
            self.fail_json(
                msg="'access' parameter is only valid for stop action",
                changed=False
            )

        # Check mode
        if self.check_mode:
            self.exit_json(
                changed=action in ["start", "stop"],
                msg=f"Action '{action}' would be executed"
            )

        result, changed = group_action(
            module=self,
            connectn=self.conn,
            authtoken=authtoken,
            tenant_id=tenant_id,
            group_id=group_id,
            action=action,
            secondary=secondary,
            primary=primary,
            access=access
        )

        self.exit_json(
            changed=changed,
            result=result
        )


def main():
    module = GroupActionModule()
    module()


if __name__ == "__main__":
    main()
