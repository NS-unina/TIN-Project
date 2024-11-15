from flask import Flask, jsonify, request
import subprocess
import docker
import os
import json

app = Flask(__name__)
client = docker.from_env()

#test structure to record container
containerList={
  "list": [
  ]
}

try:
    with open('Containers.json', 'r') as container_list:
        containerList = json.load(container_list)
except FileNotFoundError:
    container_list = open('Containers.json','w')
    container_list.write(json.dumps(containerList))
    container_list.close()
except json.JSONDecodeError as err:
    print (err)
print (containerList)


def update_container_file_list (container_name):

    try: 
        container = client.containers.get(container_name)
        
        for i, containers in enumerate(containerList["list"]):
            if containers["name"] == container_name:
                containers["state"] = container.status

        print(containerList)

        with open('Containers.json', 'w') as container_list:
            container_list.write(json.dumps(containerList))

    except docker.errors.NotFound:
        return jsonify({'Container not found': f'{container_name}'}), 404
    





@app.route('/create', methods=['POST'])
def create_container():
    data = request.json
    name = data.get('name')
    docker_image = data.get('image')
    vm_port = data.get('port')

    global containerList

    if not docker_image:
        return jsonify({"error": "Image field is needed"}), 400
    if not vm_port:
        return jsonify({"error": "Port field is needed"}), 400
    if not name:
        return jsonify({"error": "Name field is needed"}), 400
    
    #Check if name already exists
    for i, container in enumerate(containerList["list"]):
        if container["name"] == name:
            return jsonify({'Container name already in use': {name}}), 400

    
    client.containers.run(docker_image,name=name, detach=True, ports={vm_port: 2222})
    container=client.containers.get(name)

    
    new_container={
        "name": name,
        "image": docker_image,
        "state": container.status,
        "vm_port": vm_port,
        "container_port": "2222"
    }

    containerList["list"].append(new_container)

    with open('Containers.json', 'w') as container_list:
        container_list.write(json.dumps(containerList))
        
    return jsonify({"message": f"Container '{name}' successfully created!"}), 201


        

@app.route('/delete/<container_name>', methods=['DELETE'])
def delete_container(container_name):
    global containerList
    
    #delete container
    try: 
        container = client.containers.get(container_name)
    except docker.errors.NotFound:
        return jsonify({'Container not found': f'{container_name}'}), 404
        
    container.stop()  
    container.remove()

    #delete container from list
    for i, container in enumerate(containerList["list"]):
        if container["name"] == container_name:
            del containerList["list"][i]
        
            with open('Containers.json', 'w') as container_list:
                container_list.write(json.dumps(containerList))

            return jsonify({'Container deleted': f'{container_name}'}), 200

         
@app.route('/read', methods=['GET'])
def read_container():
    
    try:
        with open('Containers.json', 'r') as container_list:
            containerList = json.load(container_list)
    except FileNotFoundError:
        return jsonify({'error': 'Container list missing'}), 500
    
    return jsonify(containerList),200
    # (client.containers.list(all))






@app.route('/start/<container_name>', methods=['GET'])
def start_container(container_name):

    #Check if container exists
    try: 
        container = client.containers.get(container_name)
        container.start()
        update_container_file_list (container_name)
        return jsonify({'Container started successfully.': f'{container_name}'}), 200
    except docker.errors.NotFound:
        return jsonify({'Container not found': f'{container_name}'}), 404



@app.route('/stop/<container_name>', methods=['GET'])
def stop_container(container_name):
    
    try: 
        container = client.containers.get(container_name)
        container.stop()
        update_container_file_list (container_name)
        return jsonify({'Container stopped': f'{container_name}'}), 200

    except docker.errors.NotFound:
        return jsonify({'Container not found': f'{container_name}'}), 404
        
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)



            
