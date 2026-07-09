.. ...........................................................................
.. © Copyright IBM Corporation 2020                                          .
.. ...........................................................................

Requirements
============

A control node is any machine with Ansible installed. From the control node,
you can run commands and playbooks from a laptop, desktop, or server.
However, you cannot run **IBM PowerVC collection** on a Windows system.

A managed node is often referred to as a target node, or host, and it is managed
by Ansible. Ansible is not required on a managed node.

The nodes listed below require these specific versions of software:

Control node
------------

* `Ansible version`_: 2.14.0 or later
* `Python`_: 3.8

.. _Ansible version:
   https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html
.. _Python:
   https://www.python.org/downloads/release/latest

CLI Modules
-----------

CLI modules connect to the PowerVC Controller over SSH and have the following
additional requirements on the control node:

* ``pexpect`` — required for SSH-based interactive command execution.
  Install if not already available:

  .. code-block:: sh

     $ pip install pexpect

* The PowerVC Controller must be accessible over SSH from the control node
  using the ``pvcroot`` user.


Configuration
~~~~~~~~~~~~~

Perform the following steps from the collection directory on the control node:

.. code-block:: sh

   /root/.ansible/collections/ansible_collections/ibm/powervc/

1. Update the PowerVC Controller primary IP address in ``vars/powervc.yml``:

   .. code-block:: yaml

      ipaddress: <PowerVC_Controller_IP>

2. Update any other parameters in ``vars/powervc.yml`` as required depending
   on the operation being performed.


Ansible Vault Setup
~~~~~~~~~~~~~~~~~~~

Use Ansible Vault to securely store the ``pvcroot`` SSH password:

1. Create the vault file:

   .. code-block:: sh

      $ ansible-vault create vars/secret.yml

2. Enter a vault password when prompted and save it securely.

3. Add the following entry inside the vault file:

   .. code-block:: yaml

      pvcroot_password: <password>

4. If the file is not yet encrypted, encrypt it:

   .. code-block:: sh

      $ ansible-vault encrypt vars/secret.yml


Environment Variable
~~~~~~~~~~~~~~~~~~~~

The environment variable ``ANSIBLE_HOST_KEY_CHECKING`` must be set to
``False`` on the control node:

.. code-block:: sh

   $ export ANSIBLE_HOST_KEY_CHECKING=False

For persistence across reboots, add the variable to ``~/.bashrc`` and
source it:

.. code-block:: sh

   $ echo "export ANSIBLE_HOST_KEY_CHECKING=False" >> ~/.bashrc
   $ source ~/.bashrc
