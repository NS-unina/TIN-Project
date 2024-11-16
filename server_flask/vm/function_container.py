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
        return jsonify ({'error': f"{e}"}), 404
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
        "image": container.image,
        "state": container.status,
        "vm_port": vm_port,
        "container_port": "2222"
    }

    containerList[f"{hostname}"].append(new_container)

    with open('Containers.json', 'w') as container_list:
            container_list.write(json.dumps(containerList, indent=4))

    



def check_container_name_exist(container_name):

    try:
        with open('Containers.json', 'r') as container_list:
            containerList = json.load(container_list)
    except FileNotFoundError:
        return jsonify({'error': 'File Containers not found'}), 404   

    for entry in containerList.get(f"{hostname}", []):
        if entry.get("name") == container_name:
            return True
    return False 



def update_container_file_list (container_name):
    try:
        with open('Containers.json', 'r') as container_list:
            containerList = json.load(container_list)
    except FileNotFoundError:
        return jsonify({'error': 'File Containers not found'}), 404

    try: 
        container = client.containers.get(container_name)
        
        for i, containers in enumerate(containerList["list"]):
            if containers["name"] == container_name:
                containers["state"] = container.status

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