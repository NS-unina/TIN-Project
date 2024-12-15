from functions import *
from exceptions import *
from config import DevelopmentConfig

from flask import Flask, jsonify, request
import docker
import requests
import json
import pymongo
from flask_cors import CORS

# ********[ LOAD CONFIGURATION FROM config.py ]********
app = Flask (__name__)
app.config.from_object(DevelopmentConfig)
CORS(app,resources={r'/*':{'origins':'*'}})

DATABASE_CONNECTION = app.config['DATABASE_CONNECTION']
mongo = pymongo.MongoClient(DATABASE_CONNECTION)
database = mongo["tinDatabase"] 
containerCollection= database["containerList"]
serviceCollection= database["serviceList"]

#Server Address for network configuration 
VM_SERVER_URL=f"http://{app.config['VM_SERVER_IP']}:{app.config['VM_SERVER_PORT']}"

# #Init container list
# try:
#     containerList=init()
# except json.JSONDecodeError as e:
#     print ({'error': f"{e}"}), 400


# ********[ STARTUP ]********

    



# ********[ API ]********
@app.route('/container/create', methods=['POST'])
def create_container():
    data = request.json
    name = data.get('name')
    service_port = data.get('service_port')
    # docker_image = data.get('image')

    if not service_port:
        return jsonify({"error": "Service_port field is needed"}), 400
    
    try:

        #Check if name already exists
        if check_if_value_field_exists("name", name, containerCollection):
            return jsonify({'error': f'Container name {name} already exists.'}), 400     

        #search what image to use for the given service
        pipeline = [
        {
            "$match": {
                "services": {
                    "$elemMatch": {"service_port": f"{service_port}"}
                }
            }
        },
        {
            "$unwind": "$services"
        },
        {
            "$match": {
                "services.service_port": f"{service_port}"
            }
        },
        {
            "$sort": {"services.priority": 1}  # Sort by priority descending
        },
        {
            "$limit": 1  # Take the top result
        }
        ]
        
        result = list(serviceCollection.aggregate(pipeline))
        if not result:
            return jsonify({'error': f'No images found with service_port = {service_port}.'}), 404


        docker_image=result[0]["image"]
        container_service_port=result[0]["services"]["container_port"]
        all_services = serviceCollection.find_one(
            {"image": docker_image},
            {"_id": 0, "services": 1}
        )
        print(all_services)
        port_list={}
        for service in all_services["services"]:
            port_list[service["container_port"]]=None
            
        print(port_list)

        #if name was provided use it , otherwise use docker generated
        if name:
            container=client.containers.run(docker_image,name=name,detach=True, ports=port_list)
        else:
            container=client.containers.run(docker_image,detach=True, ports=port_list)

        # add the dynamically chosen port to the services list, and set the busy state to False
        container=client.containers.get(container.name)
        for container_port in container.attrs["NetworkSettings"]["Ports"]:
            if(container.attrs["NetworkSettings"]["Ports"][container_port]):
                for service in all_services["services"]:
                    if(service["container_port"]==container_port.split("/")[0]):
                        service["vmport"]=container.attrs["NetworkSettings"]["Ports"][container_port][0]["HostPort"]
                        service["busy"]="False"

        print("services: ",all_services)
        
        #Add item to collection
        
        new_container={
        "name": container.name,
        "image": docker_image,
        "status": container.status,
        "vm_name": hostname,
        "services": all_services["services"]
        }

        print("--------------------------------------")
        print(new_container)

        result = containerCollection.insert_one(new_container)
     
        

        return jsonify({"message": f"Container successfully created!"}), 201

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



            
