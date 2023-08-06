<img style="float: left;" src="./samples/input/cox.png">

# Network Automation Simplified - NAMS
Demonstrations are available within the Docker Container using Jupyter notebooks.

## Summary 



Suppose you must implement a network change.  You probably have a standard sequence of steps you typically follow.  You may be able to predict the steps you'll need to perform solely from experience.  You may have a formalized document detailing the sequence of tasks consisting of 4, 6 or 10 steps, depending on what you're doing. For example, your typical steps are probably similar to the pseudocode written below:

**Pre Change**
> Collect and save 'show commands' 

> Validate the router's health 

**Apply the Configuration**
> Paste in the configurations 

> Examine the 'diff'

> 'Commit'

**Post Change**

> Allow convergence

> Validate the router's health 

> Collect and save 'show commands' 

> (optional) 'confirm' or 'rollback'  


You can probably come up with several other tasks for different use-cases, all of which would likely be a slight variation of this. For instance, rather than 'commiting' the configuration, you may only want to perform a 'diff' to see what the change *would* look like. You may only want to collect 'show commands' to verify a configuration exists or to collect IGP adjacency information, or you may want to only perform health checks, because you're validating the functionality of every configured protocol on the node as you're testing a new version of code.  

Tasks like these, and the templatized sequence of these tasks, is provided by the NAMS library. The ncclient, Nornir and Jsnapy libraries are abstracted from the user to provide a simple interface for network automation.  As an introduction, explore the demo below to see a typical use-case; but don't stop there, because there are a variety of other notebooks demonstrating simple *and* advanced capabilities of NAMS.  You'll be surprised how much you can do with so few lines of code.  

## Installation
Download via **'pip'** or deploy as a **Docker Container**.  The **Docker Container is recommended**.  It allows 20+ pre-built Jupyter notebooks to be readily available via an interactive web-interface.  Without the container, the notebook samples are viewable from within the Git repository, but they will be non-interactive and will not display results.  The container will have NAMS, SSH, Jupyter and HTTP installed.  It is also configured with lab and production router hostnames, as well as Linux aliases, to simplify administration. SSH allows direct container access over the network and HTTP allows easy log retrieval.  Because containers are transferable between hosts, host X can be used for development and the container can be copied to host Y for production.  Below is a summary of why the docker container is recommended:

1. Simplifies installation 
2. Shortens development time
3. Enables sharing
4. Transferability 
5. Shell execution (see samples)

### Python Package
If you prefer not to use the Docker Container, the Python package is available on PyPi.

##### Ubuntu
```
apt-get install python3.7 python3.7-dev python3-pip
python3.7 -m pip install network-automation-simplified
```

https://pypi.org/project/network-automation-simplified/

### Docker

*Important*: the docker container will only save host data stored in the "/home" and "/svr/nams" directories.  All other data will be lost upon reboot/shutdown.

##### Linux
```
sudo apt-get update
sudo apt-get install docker docker-compose
git clone <project path>
cd cox_nams/docker && sudo bash build.sh
```

##### Mac
```
# 'brew' must be installed
brew install docker             
brew install docker-compose
brew install docker-machine
git clone <project path>
cd <project name>/docker
bash build.sh
```

##### Authentication

| Defaults |  Shell  |   SSH   | Jupyter |  HTTP |
|:--------:|:-------:|:-------:|:-------:|:-----:|
| username |  root   | admin   |   n/a   |  n/a  |
| password | install | install |  n/a    |  n/a  |
| port     |   n/a   | 10000   | 10001   | 10002 |  

##### Interfaces

| Service | Client Interface | Example                       |
|---------|------------------|-------------------------------|
| Linux   | host's shell     | docker exec -it nams bash     |
| SSH     | ssh client       | ssh \<user\>@\<host_ip\> -p 10000 |
| Jupyter | web browser      | http://\<host_ip\>:10001        |
| HTTP    | web browser      | http://\<host_ip\>:10002        |

##### Problems
Its possible that the host's docker network can assign a subnet that overlaps with devices you are attempting to connect to via nams.  In this case, static routes are required on the host. e.g. create a static route to '172.17.248.0/24' if the Docker subnet is '172.17.0.0/16' and the router is '172.17.248.1/32'. 

## Why Another Library? 
There are several existing tools written to perform network automation such as Ansible, NAPALM, Nornir, etc.  Each tool has has strengths in different categories. This Python library leverages those strengths, for a more flexible and simpler solution with less development time required.

The following Python libraries are leveraged by NAMS:

* ncclient
* Nornir
* Jsnapy 

#### ncclient
ncclient is Python library for interfacing with a NETCONF device.  ncclient is leveraged by tools like Jsnapy and Ansible.  It is vendor neutral and provides a 'raw', or unabstracted interface.  The downside of working with ncclient is that it requires the user to perform inventory management, multiprocessing, error-handling, encoding conversions, file saving, etc. 

https://ncclient.readthedocs.io/en/latest/index.html

#### Nornir
Nornir is a relatively new Python framework developed by the same creators of NAPALM and netmiko.  It's primary role is to provide inventory management and multiprocessing for APIs like ncclient, NAPALM, netmiko, and others.  One downfall of Nornir the ability to integrate Jsnapy.  This is a critical component for health checks on Juniper devices.  Because Nornir is an Open framework, a component of the framework, like inventory, can be re-used by others.  Nornir's inventory is re-used by NAMS.

https://nornir.readthedocs.io/en/stable/

#### Jsnapy
Jsnapy is an excellent Python tool for executing health checks against JunOS platforms.  It abstracts netconf requests and responses, by allowing test case definitions via a 'yaml' file.  In the yaml file, various parameters state parameters of 'show' output can be validated.  When a response is received and the test case passes, the node is considered health (vice versa for a failure).  Jsnapy uses ncclient to interface with a device.  

https://github.com/Juniper/jsnapy

#### NAPALM
NAPALM is unified API for multi-vendor network environments.  It translates high-level 'orders' into CLI commands.  Additionally, it returns output as Python objects e.g. lists, dictionaries, etc. for easy parsing. This output is the same for all vendors.  However, because there are so many results that would have to be translated into Python objects, not all commands are supported.  Additionally, some vendors have support than others.  The majority of support is in EOS systems which are uncommon to most network environments.  To workaround this, the developers allow interfacing with devices through Netconf or netmiko without translating results but while performing with error handling.  In a network domain of Juniper routers, it makes more sense to avoid the NAPALM API and leverage Juniper's Jsnapy interface with ncclient.  This is because Jsnapy cannot easily be integrated into NAPALM without developer involvement.

https://napalm.readthedocs.io/en/latest/

#### Ansible
Ansible is a YAML driven, network automation solution that supports native commands and Netconf for multiple vendors.  It has an excellent inventory system for device management and generating configurations.  YAML is a simple 'language' that users interface with; this hides the underlying Python code.  Because of YAML abstraction, Ansible sacrifices flexibility.  YAML is also not a 'programming language'.  This can make seemingly simple tasks quite difficult to 'program' or even impossible.  Another downside of Ansible is that an operation is executed on *all* routers before the next operation is performed. Examples below describe some scenarios that become quite challenging or impossible with Ansible:

1. *Group Operations*:  Executing multiple operations on a single router before moving to the next.  Additionally, user prompting at each device.


2. *Conditional Operations*: Suppose you want you want to get the configuration from all routers, find routers with 'X' configuration, and then make a change to only those select routers. 


3. *Speed*: Each operation requires a new SSH / NETCONF session.  Suppose you have two tasks (1) get configuration (2) edit configuration.  Each operation requires a new session.  

https://docs.ansible.com/
