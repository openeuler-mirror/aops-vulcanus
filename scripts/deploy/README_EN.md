# Overview

This tool is used to install aops_agent.

# Installation

- Copy or extract `aops_tools` to a node that has SSH access to all target agent nodes. Ensure the node has Internet connectivity and the openEuler 22.09 (recommended) Yum repository configured.
- All nodes scheduled for deployment must have the openEuler 22.09 EPOL Yum repository configured.
- Repository path: `/etc/yum.repos.d/openEuler.repo`

```ini
[openEuler22.09] # Official openEuler 22.09 repository
name=openEuler22.09
baseurl=https://repo.openeuler.org/openEuler-22.09/everything/$basearch/ 
enabled=1
gpgcheck=1
gpgkey=https://repo.openeuler.org/openEuler-22.09/everything/$basearch/RPM-GPG-KEY-openEuler

[Epol] # Official openEuler 22.09 EPOL repository
name=Epol
baseurl=https://repo.openeuler.org/openEuler-22.09/EPOL/main/$basearch/ 
enabled=1
gpgcheck=1
gpgkey=https://repo.openeuler.org/openEuler-22.09/OS/$basearch/RPM-GPG-KEY-openEuler

```

# Configuration

## Host Information

Modify the `conf/import_host.xls` file. The table lists the agent information for each node to be deployed. The fields are described as follows.

|Field|Description|
|----|----|
|host_name|Host name of the target node, for example, `localhost`.|
|ansible_host|IP address of the target node.|
|ansible_user|User name for SSH login to the target node.|
|ansible_ssh_pass|Password for SSH login to the target node.|
|ansible_become_user|User for privilege escalation on the target node.|
|ansible_become_method|Method used for privilege escalation on the target node.|
|ansible_become_password|Password required for privilege escalation on the target node.|
|web_username|Frontend login user name.|
|web_password|Frontend login user password.|
|aops_host_name|Custom alias for the target node.|
|host_group_name|Host group the target node will join. Ensure the group exists or create it on the frontend first.|
|manager_ip|Listening IP address for the RESTful API on the management node.|
|management|Indicates whether the target node is a management node.|
|manager_port|Listening port for the RESTful API on the management node.|
|agent_port|Listening port for the RESTful API on the target node.|

In the `import_host.xls` file, you need to enter the agent login password and frontend login password. After the deployment is complete, clear or delete the passwords from the host in a timely manner.

# Execution

Run the following scripts:

```shell
dos2unix install_aops.sh
sh install_aops.sh
```
