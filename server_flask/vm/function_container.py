import docker
import json
from flask import jsonify
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
    except json.JSONDecodeError as e:
        return jsonify ({'error': f"{e}"}), 400
    print (containerList)


# Create item in container list
def create_item_container_list(container, vm_port):

    try:
        with open('Containers.json', 'r') as container_list:
            containerList = json.load(container_list)
    except FileNotFoundError:
        return jsonify({'error': 'File Containers not found'}), 404

    new_container={
        "name": container.name,
        "image": str(container.image),
        "state": container.status,
        "vm_port": vm_port,
        "container_port": "2222"
    }

    containerList[f"{hostname}"].append(new_container)
    print (containerList)
    
    with open('Containers.json', 'w') as container_list:
            container_list.write(json.dumps(containerList, indent=4))

    

#Search value of a field in dictionary
def search_container_by_field(field, value):

    try:
        with open('Containers.json', 'r') as container_list:
            containerList = json.load(container_list)
    except FileNotFoundError:
        return jsonify({'error': 'File Containers not found'}), 404   

    for entry in containerList.get(f"{hostname}", []):
        if entry.get(f"{field}") == value:
            return True
    return False   


def update_container_field (container_name, field, value):
    try:
        with open('Containers.json', 'r') as container_list:
            containerList = json.load(container_list)
    except FileNotFoundError:
        return jsonify({'error': 'File Containers not found'}), 404

    try: 
        for entry in containerList.get(f"{hostname}", []):
            if entry.get(f"name") == container_name:
                entry[f"{field}"] = value

        print(containerList)

        with open('Containers.json', 'w') as container_list:
            container_list.write(json.dumps(containerList, indent=4))

    except docker.errors.NotFound:
        return jsonify({'error': "Container not found: f'{container_name}'"}), 404
    

#Delete from dictionary
def delete_from_dictionary(container_name):
    
    try:
        with open('Containers.json', 'r') as container_list:
            containerList = json.load(container_list)
    except FileNotFoundError:
        return jsonify({'error': 'File Containers not found'}), 404

    containerList[f"{hostname}"] = [entry for entry in containerList.get(f"{hostname}", []) if entry.get("name") != container_name]
    
    with open('Containers.json', 'w') as container_list:
        container_list.write(json.dumps(containerList, indent=4))