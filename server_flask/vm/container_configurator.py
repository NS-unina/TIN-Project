from function_container import *
from flask import Flask, jsonify, request
import docker
import json
from flask_cors import CORS

app = Flask(__name__)

CORS(app,resources={r'/*':{'origins':'*'}})

#Init container list
try:
    containerList=init()
except json.JSONDecodeError as e:
    print ({'error': f"{e}"}), 400


@app.route('/create', methods=['POST'])
def create_container():
    data = request.json
    name = data.get('name')
    docker_image = data.get('image')
    vm_port = data.get('vm_port')

    if not docker_image:
        return jsonify({"error": "Image field is needed"}), 400
    if not vm_port:
        return jsonify({"error": "Port field is needed"}), 400
    if not name:
        return jsonify({"error": "Name field is needed"}), 400
    
    try:

        #Check if name already exists
        if check_if_value_field_exists("name", name):
            return jsonify({'error': f'Container name {name} already exists.'}), 400

        #Check if port already exists
        if check_if_value_field_exists("vm_port", vm_port):
            return jsonify({'error': f'Container port {vm_port} already in use.'}), 400
        
        client.containers.run(docker_image,name=name, detach=True, ports={2222:vm_port})
        container=client.containers.get(name)
        create_item_container_list(container, vm_port)

        return jsonify({"message": f"Container '{name}' successfully created!"}), 201

    except ContainerFileNotFound as e:
        return jsonify ({'error': f"{e.message}"}), e.error_code
    except docker.errors.APIError as e:
        return jsonify({'error': f'{e}'})
        
        

@app.route('/delete/<container_name>', methods=['DELETE'])
def delete_container(container_name):

    try:
        #Check if name already exists
        if not check_if_value_field_exists("name", container_name):
            return jsonify({'error': f"Container name {container_name} doesn't exists."})

        #delete container
        container = client.containers.get(container_name)
        container.stop()  
        container.remove()
        delete_from_dictionary(container_name)

        return jsonify({"message": f"Container '{container_name}' successfully deleted!"}), 200
    
    except ContainerFileNotFound as e:
        return jsonify ({'error': f"{e.message}"}), e.error_code
    except docker.errors.NotFound:
        return jsonify({'Container not found': f'{container_name}'}), 404
    

         
@app.route('/read', methods=['GET'])
def read_container():
    try:
        containerList= get_all_container_dictionary() 
        return jsonify(containerList), 200
    
    except ContainerFileNotFound as e:
        return jsonify ({'error': f"{e.message}"}), e.error_code



@app.route('/start/<container_name>', methods=['POST'])
def start_container(container_name):

    #Check if container exists
    try: 
        container = client.containers.get(container_name)
        container.start()
        update_container_field (container_name, "status", "running")
        return jsonify({'Container started successfully.': f'{container_name}'}), 200
    
    except ContainerFileNotFound as e:
        return jsonify ({'error': f"{e.message}"}), e.error_code
    except docker.errors.NotFound:
        return jsonify({'Container not found': f'{container_name}'}), 404

    

@app.route('/stop/<container_name>', methods=['POST'])
def stop_container(container_name):
    
    try: 
        container = client.containers.get(container_name)
        container.stop()
        update_container_field (container_name, "status", "exited")
        return jsonify({'Container stopped': f'{container_name}'}), 200

    except ContainerFileNotFound as e:
        return jsonify ({'error': f"{e.message}"}), e.error_code
    except docker.errors.NotFound:
        return jsonify({'Container not found': f'{container_name}'}), 404
        
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)



            
