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


@app.route('/container/create', methods=['POST'])
def create_container():
    data = request.json
    name = data.get('name')
    docker_image = data.get('image')
    vm_port = data.get('vm_port')

    if not docker_image:
        return jsonify({"error": "Image field is needed"}), 400
    
    try:

        #Check if name already exists
        if check_if_value_field_exists("name", name):
            return jsonify({'error': f'Container name {name} already exists.'}), 400

        #Check if port already exists
        if check_if_value_field_exists("vm_port", vm_port):
            return jsonify({'error': f'Container port {vm_port} already in use.'}), 400
        

        #if name  or vm_port was provided use it , otherwise use docker generated
        if name and vm_port:
            container=client.containers.run(docker_image,name=name,detach=True, ports={"2222/tcp":vm_port})
        elif name:
            container=client.containers.run(docker_image,name=name,detach=True, ports={"2222/tcp":None})
        elif vm_port:
            container=client.containers.run(docker_image,detach=True, ports={"2222/tcp":vm_port})
        else:
            container=client.containers.run(docker_image,detach=True, ports={"2222/tcp":None})

        #refresh to get the assigned port
        container=client.containers.get(container.name)
        vm_port= container.attrs["NetworkSettings"]["Ports"]["2222/tcp"][0]["HostPort"]

        new_container=create_item_container_list(container, vm_port)

        return jsonify({"message": f"Container successfully created!","container":new_container}), 201

    except ContainerFileNotFound as e:
        return jsonify ({'error': f"{e.message}"}), e.error_code
    except docker.errors.APIError as e:
        return jsonify({'error': f'{e}'})
        
        

@app.route('/container/delete/<container_name>', methods=['DELETE'])
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
    

         
@app.route('/container/list', methods=['GET'])
def read_container():
    try:
        containerList= get_all_container() 
        return jsonify(containerList), 200
    
    except ContainerFileNotFound as e:
        return jsonify ({'error': f"{e.message}"}), e.error_code



@app.route('/container/start/<container_name>', methods=['POST'])
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

    

@app.route('/container/stop/<container_name>', methods=['POST'])
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
    

@app.route('/container/ping', methods=['GET'])
def ping():
    return jsonify("server running"), 200


@app.route('/container/count', methods=['GET'])
def container_number():
    containerList = get_all_container()
    return jsonify({sum(len(containers) for containers in containerList.values())}), 200

    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)



            
