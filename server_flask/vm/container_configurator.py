from function_container import *
from flask import Flask, jsonify, request
import docker
import json

app = Flask(__name__)

#Init container list
containerList=init()



@app.route('/create', methods=['POST'])
def create_container():
    data = request.json
    name = data.get('name')
    docker_image = data.get('image')
    vm_port = data.get('port')

    if not docker_image:
        return jsonify({"error": "Image field is needed"}), 400
    if not vm_port:
        return jsonify({"error": "Port field is needed"}), 400
    if not name:
        return jsonify({"error": "Name field is needed"}), 400
    
    #Check if name already exists
    if search_container_by_field("name", name):
        return jsonify({'error': f'Container name {name} already exists.'}), 400

    #Check if port already exists
    if search_container_by_field("vm_port", vm_port):
        return jsonify({'error': f'Container port {vm_port} already in use.'}), 400
    
    try:
        client.containers.run(docker_image,name=name, detach=True, ports={2222:vm_port})
        container=client.containers.get(name)
        create_item_container_list(container, vm_port)
    except docker.errors.APIError as e:
        return jsonify({'error': f'{e}'})
        
    return jsonify({"message": f"Container '{name}' successfully created!"}), 201
        

@app.route('/delete/<container_name>', methods=['DELETE'])
def delete_container(container_name):

    #Check if name already exists
    if not search_container_by_field("name", container_name):
        return jsonify({'error': f"Container name {container_name} doesn't exists."})
    
    #delete container
    try: 
        container = client.containers.get(container_name)
        container.stop()  
        container.remove()
        delete_from_dictionary(container_name)
        return jsonify({"message": f"Container '{container_name}' successfully deleted!"}), 200
    except docker.errors.NotFound:
        return jsonify({'Container not found': f'{container_name}'}), 404
    

         
@app.route('/read', methods=['GET'])
def read_container():
    
    try:
        with open('Containers.json', 'r') as container_list:
            containerList = json.load(container_list)
    except FileNotFoundError:
        return jsonify({'error': 'Container list missing'}), 500
    
    return jsonify(containerList), 200



@app.route('/start/<container_name>', methods=['POST'])
def start_container(container_name):

    #Check if container exists
    try: 
        container = client.containers.get(container_name)
        container.start()
        update_container_field (container_name, "status", "running")
        return jsonify({'Container started successfully.': f'{container_name}'}), 200
    except docker.errors.NotFound:
        return jsonify({'Container not found': f'{container_name}'}), 404

    

@app.route('/stop/<container_name>', methods=['POST'])
def stop_container(container_name):
    
    try: 
        container = client.containers.get(container_name)
        container.stop()
        update_container_field (container_name, "status", "exited")
        return jsonify({'Container stopped': f'{container_name}'}), 200

    except docker.errors.NotFound:
        return jsonify({'Container not found': f'{container_name}'}), 404
        
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)



            
