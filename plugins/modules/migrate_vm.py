from ansible_collections.openstack.cloud.plugins.module_utils.openstack import OpenStackModule
from ansible_collections.ibm.powervc.plugins.module_utils.crud_migrate import migrate_ops


class MigrateVMModule(OpenStackModule):
    argument_spec = dict(
        name=dict(required=True),
        host=dict(required=False),
    )
    module_kwargs = dict(
        supports_check_mode=True
    )

    def run(self):
        authtoken = self.conn.auth_token
        tenant_id = self.conn.session.get_project_id()
        vm_name = self.params['name']
        host = self.params['host']
        vm_id = self.conn.compute.find_server(vm_name, ignore_missing=False).id
        try:
            data = {"os-migrateLive": {"host": host, "block_migration": "false", "disk_over_commit": "true"}}
            res = migrate_ops(self, self.conn, authtoken, tenant_id, vm_id, host, data)
            self.exit_json(changed=True, result=res)
        except Exception as e:
            self.fail_json(msg=f"An unexpected error occurred: {str(e)}", changed=True)


def main():
    module = MigrateVMModule()
    module()


if __name__ == '__main__':
    main()
