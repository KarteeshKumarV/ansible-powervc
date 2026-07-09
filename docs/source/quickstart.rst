.. ...........................................................................
.. © Copyright IBM Corporation 2020                                          .
.. ...........................................................................

Quickstart
==========

After installing the collection outlined in the  `installation`_ guide, you
can access the collection and the ansible-doc covered in the following topics:

.. _installation:
   installation.html

ibm.powervc
--------------

After the collection is installed, you can access the collection content for a
playbook by referencing the namespace ``ibm`` and the collection's fully
qualified name ``powervc``. For example:

.. code-block:: yaml

  - name: VM Capture Playbook
    hosts: all
    gather_facts: no
    vars:
     auth:
      auth_url: https://{{ PowerVC }}:5000/v3
      project_name: '{{ powervc_project }}'
      username: '{{ powervc_user }}'
      password: '{{ powervc_password }}'
      project_domain_name: Default
      user_domain_name: Default
    tasks:
       - name: Perform VM Capture Operations
         ibm.powervc.capture_vm:
            auth: "{{ auth }}"
            name: "ansible_vm"
            image_name: "test_Image"
            validate_certs: no
         register: result
       - debug:
            var: result


In Ansible 2.14.0, the ``collections`` keyword was added to reduce the need
to refer to the collection repeatedly. For example, you can use the
``collections`` keyword in your playbook:

.. code-block:: yaml


ibm.powervc.cli
---------------

CLI modules connect to the PowerVC Controller over SSH and are referenced
using the ``ibm.powervc.cli`` namespace. For example, to monitor PowerVC
node resources using the ``pvcmon`` CLI module:

.. code-block:: yaml

   ---
   - name: "Monitor PowerVC Node Resources (with interval)"
     hosts: localhost
     vars_files:
       - vars/powervc.yml
       - vars/secret.yml

     tasks:
       - name: "Monitor resource usage with specified interval"
         ibm.powervc.cli.pvcmon:
           login_host: "{{ ipaddress }}"
           login_user: "{{ pvc_user }}"
           login_password: "{{ pvcroot_password }}"
           resource: "{{ resource }}"
           interval: "{{ interval }}"
         register: result

       - name: "Display monitoring output"
         debug:
           var: result.stdout_lines

The variables ``ipaddress``, ``pvc_user``, ``resource``, ``interval`` 
are defined in ``vars/powervc.yml``.
The variable ``pvcroot_password`` is stored securely in the Ansible Vault file
``vars/secret.yml``. See the `installation`_ guide for vault setup details.


ansible-doc
-----------

Modules included in this collection provide additional documentation that is
similar to a UNIX-like operating system man page (manual page). This
documentation can be accessed from the command line by using the
``ansible-doc`` command.

Here's how to use the ``ansible-doc`` command after you install the
**IBM PowerVC collection**: ``ansible-doc ibm.powervc.capture_vm``

For CLI modules, use the fully qualified module name including the ``cli``
sub-namespace. For example: ``ansible-doc ibm.powervc.cli.pvcmon``

For more information on using the ``ansible-doc`` command, refer
to the `Ansible guide`_.

.. _Ansible guide:
   https://docs.ansible.com/ansible/latest/cli/ansible-doc.html#ansible-doc

Connection Method
-----------------

Ansible communicates with remote machines over the SSH protocol. By default, Ansible uses native OpenSSH and connects to remote machines and communicates from the control node via SSH tunnel.

In case of PowerVC collection, it uses an API-based execution model in this case, the Ansible collection should use the local connection type, meaning all API calls are made from the control node rather than running code on the PowerVC host.

CLI modules use a direct SSH connection to the PowerVC Controller (as the
``pvcroot`` user) to execute native PowerVC CLI commands. The ``hosts`` value
in CLI playbooks should be set to ``localhost`` so that all SSH connections
are initiated from the Ansible controller. The environment variable
``ANSIBLE_HOST_KEY_CHECKING`` must be set to ``False`` on the Ansible controller.
