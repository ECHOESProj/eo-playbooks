# Provisioning, configuration management, and application-deployment for the EO service 

[Ansible](https://www.Ansible.com/) and [Vagrant](https://www.vagrantup.com/) are used to automate the 
setup of development and deployment machines for the Earth Observation Service. 
For and overview of the Earth Observation Service see [Earth Observation Docs](https://github.com/ECHOESProj/eo-docs) 
for an overview of the EO Service.

Ansible uses no agents, so it is not necessary to install software on the remote machine in order for it to work. 
The desired state of the remote machines (hosts) are defined in "Playbooks".
These are written in YAML, which describe your automation jobs in a way that is easily human-readable.
See [Ansible Basic Concepts](https://docs.Ansible.com/Ansible/latest/network/getting_started/basic_concepts.html#id1)
for Ansible concepts and terminology.

[Vagrant](https://www.vagrantup.com/) is used to provision the VMs on the local machine, and it runs the Playbook
to perform the above. 
Vagrant is used to check that the Playbook is working, and it can be used to create
a VM for local development work.
However, if you just wish to configure/deploy a remote machine, Vagrant is not required.  

The host machines could be a remote VMs or the local machine.
It has been tested with Ubuntu 20.04 hosts.  

The Playbooks perform the following:
* install system packages
* install Python requirements
* copy keys over
* copy the credentials over
* set environment variables
* install Docker
* deploy Docker images
* Install JupyterLab (dev machine only)

Ansible does not (directly) run on Windows. 
However, if you are using Windows, you can WSL for the control node.
The machine from which you run the Ansible CLI tools (ansible-playbook, Ansible-vault and etc.).
  

## Prerequisites

Sentinel Hub and CREODIAS accounts are required for full functionality. 
The Playbook works out-of-the-box for CREODIAS, but can be adapted to run on AWS.

On the [control node](https://docs.ansible.com/ansible/latest/network/getting_started/basic_concepts.html#control-node)
(i.e. your local machine):

1. [Install WSL2](https://docs.microsoft.com/en-us/windows/wsl/install) (for Windows users).
Also, refer to [Docker Desktop WSL 2 backend](https://docs.docker.com/desktop/windows/wsl/) 
if you wish to use Docker on WSL, in order to deploy the Docker containers on the local machine. 

2. Clone this repo with 

    git clone git@github.com:ECHOESProj/eo-playbooks.git

3. [Install Ansible](https://docs.Ansible.com/Ansible/latest/installation_guide/intro_installation.html#installing-Ansible-on-ubuntu)
Ansible can be installed with:


    pip install --user Ansible

4. Install Vagrant (optional):

   * [Install Virtual Box](https://www.virtualbox.org/wiki/Downloads)
   * [Install Vagrant on WSL2](https://blog.thenets.org/how-to-run-vagrant-on-wsl-2/) 
 

## First-time Setup

### Set the variables

In order to run the Playbook, the credentials should be given in the *group_vars* directory,
and the host names should be given in the *hosts* file.

Templates files are provided for *hosts* and *group_vars*. 
Add the IPs of the host machines to hosts. 
Set the variables in *group_vars/all* as described bellow.  

#### Sentinel Hub Credentials

Populate the sh_instance_id, sh_client_id and sh_client_secret variables,
in group_vars/all,
with those [obtained from your Sentinel Hub account](https://apps.sentinel-hub.com/dashboard/#/account/settings).
The sh_instance_id variable corresponds to *User ID* and sh_client_id corresponds to *OAuth clients ID*
in the Sentinel Hub website.

#### CREODIAS credentials

Follow [these instructions](https://creodias.eu/-/how-to-generate-ec2-credentials-?inheritRedirect=true&redirect=%2Ffaq-s3)
to write to an S3 compatible bucket on CREODIAS and populate *s3_aws_access_key_id* and *s3_aws_secret_access_key*, 
in group_vars/all, with the credentials that have been generated.

      openstack ec2 credentials list


```text
+----------------------------------+----------------------------------+----------------------------------+----------------------------------+
| Access                           | Secret                           | Project ID                       | User ID                          |
+----------------------------------+----------------------------------+----------------------------------+----------------------------------+
| ******************************** | ******************************** | ******************************** | ******************************** |
+----------------------------------+----------------------------------+----------------------------------+----------------------------------+
```


### Jupyter Lab password

Run the following Python code to generate the password:
```python3
      from notebook.auth import passwd
      my_password = "password-goes-here"
      hashed_password = passwd(passphrase=my_password)
      print(hashed_password)
```
Put it in group_vars/all under jupyter_notebook_pass.

#### Jupyter Lab Keys

The Playbook installs Jupyter Lab on the development VM (but not the production).
Jupyter Lab is accessed via the browser.
The Playbook copies the SSL keys across, 
[to enable HTTPS](https://jupyterhub.readthedocs.io/en/stable/getting-started/security-basics.html).
In the Ubuntu terminal, they can be generated with:

      openssl req -x509 -newkey rsa:4096 -keyout jupyter.pem -out jupyter.pem -sha256 -days 365

The keys should be named jupyter.key and jupyter.pem and placed as follows:
   
      eo-playbooks/roles/jupyter/files/jupyter.key
      eo-playbooks/roles/jupyter/files/jupyter.pem


### The SSH key 

If a key has not already been created for the VM, do so with the following command:
 
    ssh-keygen

Name the key is named "eo-stack.key" and set the permissions with:

    sudo chmod 600 ~/.ssh/eo-stack.key

Place the SSH key(s) for the hosts (i.e. the remote machines that will be provisioned) in ~/.ssh/. 
The key name(s) should correspond to those specified in the hosts file.
Check that you can SSH into VMs using this key(s).

## Usage

The Playbook can be run against a previously provisioned VM. 
In this case, the Playbook will ensure packages are updated, 
and the required files are copied across, etc.  

To provision a new VM, ensure that its IP is added to the hosts file.

An existing VM on CREODIAS can be rebuilt by clicking on the dropdown for the VM and selecting "Rebuild instance".
Be aware that any data on the VM will be destroyed, including any Jupyter Notebooks that have been created. 

Execute the Playbook with:

    ansible-playbook -i hosts site.yml

This will provision all the machines given in hosts. Provision just the dev machines with:

    ansible-playbook -i hosts site.yml --limit dev

Or, provision just the production machines (deploying the Docker service) with "--limit prod".

You may encounter the following message if you rebuild the instance:

      WARNING: REMOTE HOST IDENTIFICATION HAS CHANGED!

The error can be rectified with:

      ssh-keygen -f ~/.ssh/known_hosts -R <ip.of.vm>

## Deployment keys (For Private Repos)

Deployment keys are *not* required for public repos. 

The deployment keys should be added to:
   
      eo-playbooks/roles/common/files/github_keys

and named as follows:
* eo_io_rsa
* eoian_rsa
* eo_custom_scripts_rsa
* eo_processors_rsa
* eo_websockets_server_rsa
* eo_stack_rsa
* eo_notebooks_rsa

The playbook will copy the keys over, to enable cloning of the repos. 

When using [deployment keys](https://docs.github.com/en/developers/overview/managing-deploy-keys),
use the "never" tag, e.g.

    ansible-playbook -i hosts site.yml --tags all,never

## Run using Vagrant

[Vagrant](https://www.vagrantup.com/) is used to set up the EO Service on a local VM.
This is useful for testing the Playbook,
or creating an isolated environment to run the EO Service. 

The Ansible Playbook site.yml is used to install the EO service on
a VM or on a local machine. 

    vagrant up --provision

Then SSH into it with:

    vagrant ssh
