# NS Unina - Threat Intelligence Network

The purpose of this project is to create a Threat Intelligence Network leveraging Software Defined Networking (SDN) principles in conjunction with Moving Target Defense and decoy techniques.
This work also introduces a flexible management system that allows for automatic deployment, setup, and real-time monitoring of honeypots


<img src="https://github.com/user-attachments/assets/56948c74-e5de-4f1e-a2e1-cc25ca8981f0" width="200">

WORK IN PROGRESS
## Installation

### Requirements


In order to execute the project you need to install Open vSwitch, Vagrant, VirtualBox

### Setup

#### Create and Activate the virtual environment:

Inside the directory:

```
python3 -m venv <name_of_the_environment>
source bin/activate
```

#### Install the Requirements:

Backend Requirements:

```
cd /server_flask
pip install -r requirements.txt
```

Frontend Requirements:

```
cd /client
nodeenv -p
npm install
```

#### Run the backend servers

```
cd /server_flask
flask --app network_configurator.py -p 5001
```

```
cd /server_flask
flask --app vm_configurator.py -p 5000
```

#### Run the frontend server

```
cd /server_flask/client
npm run dev
```

## Architecture

![architecture](https://github.com/user-attachments/assets/83c9e3fd-7039-4325-973b-8cbe2c8d7749)


## Authors

- [Andrea Dinetti](https://github.com/AndreaDino)
- [Marika Sasso](https://github.com/MarikaSasso)
