from exception_container import *
import docker
import json
import socket


client = docker.from_env()
hostname = socket.gethostname()

def init():
    containerList={
        f"{hostname}": [
        ]
    }
    
    try:
        with open('Containers.json', 'r') as container_list:
            containerList = json.load(container_list)
    except FileNotFoundError:
        container_list = open('Containers.json','w')
        container_list.write(json.dumps(containerList, indent=4))
        container_list.close()
    print (containerList)


# Create item in container list
def create_item_container_list(container, vm_port):

    try:
        with open('Containers.json', 'r') as container_list:
            containerList = json.load(container_list)
    except FileNotFoundError:
        raise ContainerFileNotFound ("Container file not found.", error_code=404)

    new_container={
        "name": container.name,
        "image": str(container.image),
        "status": container.status,
        "vm_port": vm_port,
        "container_port": "2222"
    }

    containerList[f"{hostname}"].append(new_container)
    print (containerList)
    
    with open('Containers.json', 'w') as container_list:
            container_list.write(json.dumps(containerList, indent=4))

    return new_container

#Search value of a field in dictionary
def check_if_value_field_exists(field, value):

    try:
        with open('Containers.json', 'r') as container_list:
            containerList = json.load(container_list)
    except FileNotFoundError:
        raise ContainerFileNotFound ("Container file not found.", error_code=404)

    for entry in containerList.get(f"{hostname}", []):
        if entry.get(f"{field}") == value:
            return True
    return False   


def update_container_field (container_name, field, value):
    try:
        with open('Containers.json', 'r') as container_list:
            containerList = json.load(container_list)
    except FileNotFoundError:
        raise ContainerFileNotFound ("Container file not found.", error_code=404)

    for entry in containerList.get(f"{hostname}", []):
        if entry.get(f"name") == container_name:
            entry[f"{field}"] = value
    print(containerList)

    with open('Containers.json', 'w') as container_list:
        container_list.write(json.dumps(containerList, indent=4))
    

#Delete from dictionary
def delete_from_dictionary(container_name):
    try:
        with open('Containers.json', 'r') as container_list:
            containerList = json.load(container_list)
    except FileNotFoundError:
        raise ContainerFileNotFound ("Container file not found.", error_code=404)

    containerList[f"{hostname}"] = [entry for entry in containerList.get(f"{hostname}", []) if entry.get("name") != container_name]
    
    with open('Containers.json', 'w') as container_list:
        container_list.write(json.dumps(containerList, indent=4))


def get_all_container():
    try:
        with open('Containers.json', 'r') as container_list:
            containerList = json.load(container_list)
    except FileNotFoundError:
        raise ContainerFileNotFound ("Container file not found.", error_code=404)
    
    return containerList