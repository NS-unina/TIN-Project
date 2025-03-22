# NS Unina - Threat Intelligence Network

The purpose of this project is to create a Threat Intelligence Network leveraging Software Defined Networking (SDN) principles in conjunction with Moving Target Defense and decoy techniques.
This work also introduces a flexible management system that allows for automatic deployment, setup, and real-time monitoring of honeypots


<img src="https://github.com/user-attachments/assets/997cf887-b93a-4ece-bd58-0678ce42ff1e" width="200">

WORK IN PROGRESS
## Installation

### Requirements


In order to execute the project you need to install Open vSwitch, Vagrant, VirtualBox, Python3, ONOS, Docker.

### Setup Virtual Environments

#### Create and Activate the virtual environment:

Inside the main directory create three virtual environment (named: *tin_services*, *tin_manager_server* and *client*):

```
python3 -m venv <name_of_the_environment>
```

#### Install the Requirements:

For all the three virtual environment, install the requirements:

```
cd /<name_of_the_environment>
pip install -r requirements.txt
```

Additionally, inside the *client* folder, install also the frontend requirements:

```
cd /client
nodeenv -p
npm install
```

#### Install Database
Run the following command to pull and run the mongodb docker image:
```
docker pull mongo:latest
docker volume create mongodata
docker run -d -v tincan:/data/db -p 27017:27017 --name tindb -e MONGO_INITDB_ROOT_USERNAME=<user> -e MONGO_INITDB_ROOT_PASSWORD=<passwd> mongo:latest --port 27017
```

## Startup

### Run the backend servers

#### Virtual Machine configurator
```
cd /tin_services
source bin/activate
flask --app vm_configurator.py -p 5000
```

#### Network configurator
```
cd /tin_services
source bin/activate
flask --app network_configurator.py -p 5001
```

#### TIN Manager
```
cd /tin_manager_server
source bin/activate
flask --app tin_manager.py -p 5003
```


### Run the frontend server

```
cd /client
source bin/activate
npm run dev
```

## Architecture

![architecture](https://github.com/user-attachments/assets/83c9e3fd-7039-4325-973b-8cbe2c8d7749)


## Authors

- [Andrea Dinetti](https://github.com/AndreaDino)
- [Marika Sasso](https://github.com/MarikaSasso)
