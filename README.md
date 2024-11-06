# NS Unina - Threat Intelligence Network

The purpose of this project is to create a Threat Intelligence Network leveraging Software Defined Networking (SDN) principles in conjunction with Moving Target Defense and decoy techniques.
This work also introduces a flexible management system that allows for automatic deployment, setup, and real-time monitoring of honeypots

WORK IN PROGRESS

## Installation

### Requirements

In order to execute the project you need to install Open vSwitch, Vagrant, Libvirt

### Setup

#### Create and Activate the virtual environment:

```
python3 -m venv <name_of_the_environment>
source bin/activate
```

#### Install the Requirements:

```
pip install -r requirements.txt
```

#### Run the flask server

```
cd /server_flask
flask run
```

## Architecture

## Authors

- [Andrea Dinetti](https://github.com/AndreaDino)
- [Marika Sasso](https://github.com/MarikaSasso)
