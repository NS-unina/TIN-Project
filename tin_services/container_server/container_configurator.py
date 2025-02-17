from functions import *
from exceptions import *
from validation_schemas import *

from config import DevelopmentConfig

from flask import Flask, jsonify, request
import docker
import requests
import json
import pymongo
from flask_cors import CORS

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

# ********[ LOAD CONFIGURATION FROM config.py ]********
app = Flask (__name__)
app.config.from_object(DevelopmentConfig)
CORS(app,resources={r'/*':{'origins':'*'}})

try:
    DATABASE_CONNECTION = app.config['DATABASE_CONNECTION']
    mongo = pymongo.MongoClient(DATABASE_CONNECTION, serverSelectionTimeoutMS=10000)
    database = mongo["tinDatabase"] 
    containerCollection= database["containerList"]
    serviceCollection= database["serviceList"]
except pymongo.errors.ConnectionFailure as e:
    print('error: Connection to database failed.')

#Server Address for network configuration 
VM_SERVER_URL=f"http://{app.config['VM_SERVER_IP']}:{app.config['VM_SERVER_PORT']}"


# ********[ STARTUP ]********

    


# Configuration of BackgroundScheduler
scheduler = BackgroundScheduler()
scheduler.start()
scheduler.add_job(lambda: sync_container(containerCollection), trigger=IntervalTrigger(seconds=15))



# ********[ API ]********
@app.route('/container/create', methods=['POST'])
def create_container():
    data = request.json

    try:
        validated_data = ContainerSchema().load(data)
    except ValidationError as e:
        return jsonify({"error": f"{e}"}), 400

    name = data.get('name')
    service_port = data.get('service_port')


    try:   
        #Check if name already exists
        if check_if_value_field_exists("name", name, containerCollection):
           return jsonify({'error': f'Container name {name} already exists.'}), 400        
	
        #Search what image to use for the given service
        container_data = search_image_by_service (service_port, serviceCollection)
        if not container_data:
            return jsonify({'error': f'No image found with service_port = {service_port}.'}), 404
        
        #Select docker images
        docker_image=container_data[0]["image"]
        print(f"Image: {docker_image}")

        #previous query returns only the searched service, we need all the services to map them for future use
        all_services = serviceCollection.find_one({"image": docker_image}, {"_id": 0, "services": 1})

        #Parameters 
        port_list={}
        volumes={}
        environment_variables={}
        #environment = {"ENV_VAR_1": "value1",    "ENV_VAR_2": "value2"}
        #volumes = {"/path/on/host": {"bind": "/path/in/container", "mode": "rw"}


        print(all_services)
        for service in all_services["services"]:
            port_list[service["container_port"]]=None
        
        for volume in container_data[0]["volumes"]:
            volumes[volume["host"]] = {"bind":volume["container"],"mode":"rw"}

        for variable in container_data[0]["environment"]:
            environment_variables[variable["name"]]=variable["value"]

        print("-----------------")
        print (volumes)
        #if name was provided use it , otherwise use docker generated
        if name:
            container=client.containers.run(docker_image,name=name,detach=True, ports=port_list,volumes=volumes,environment=environment_variables)
        else:
            container=client.containers.run(docker_image,detach=True, ports=port_list,volumes=volumes,environment=environment_variables)

        # add the dynamically chosen port to the services list, and set the busy state to False
        container=client.containers.get(container.name)
        print(f"Container name: {container.name}")
        for container_port in container.attrs["NetworkSettings"]["Ports"]:
            if(container.attrs["NetworkSettings"]["Ports"][container_port]):
                for service in all_services["services"]:
                    if(service["container_port"]==container_port.split("/")[0]):
                        service["vm_port"]=container.attrs["NetworkSettings"]["Ports"][container_port][0]["HostPort"]
                        service["busy"]="False"
        
        #Add item to collection
        container=create_item_list(container, all_services, containerCollection)

        return jsonify({"message": f"Container successfully created!","container": container}), 201

    except FailedInsertion as e:
        return jsonify ({'error': f"{e.message}"}), 500
    except pymongo.errors.ConnectionFailure as e:
        return jsonify({'error': 'Connection to database failed.'}), 500
    except docker.errors.APIError as e:
        return jsonify({'error': f'{e}'}), 500
        
        

@app.route('/container/delete/<container_name>', methods=['DELETE'])
def delete_container(container_name):

    try:
        validated_data = ContainerNameSchema().load({"container_name":container_name})
    except ValidationError as e:
        return jsonify({"error": f"{e}"}), 400


    try:
        #Check if name already exists
        if not check_if_value_field_exists("name", container_name, containerCollection):
            return jsonify({'error': f"Container name {container_name} doesn't exists."}),404

        #delete container
        container = client.containers.get(container_name)
        container.stop()  
        container.remove()
        delete_from_db(container_name,containerCollection)

        return jsonify({"message": f"Container '{container_name}' successfully deleted!"}), 200
    
    except ItemNotFound as e:
        return jsonify ({'error': f"{e.message}"}), 404
    except pymongo.errors.ConnectionFailure as e:
        return jsonify({'error': 'Connection to database failed.'}), 500
    except docker.errors.NotFound:
        return jsonify({'Container not found': f'{container_name}'}), 404
    except Exception as e :
        return jsonify ({'error': f"{e}"})


@app.route('/container/delete/byport/<vm_port>', methods=['DELETE'])
def delete_container_by_port(vm_port):
    
    try:
        validated_data = VMPortSchema().load({"vm_port":vm_port})
    except ValidationError as e:
        return jsonify({"error": f"{e}"}), 400
    
    try:
        container_name = get_container_by_vm_port(vm_port, containerCollection)["name"]
        print (container_name)

        container = client.containers.get(container_name)
        container.stop()  
        container.remove()
        delete_from_db(container_name,containerCollection)
        return jsonify({"message": f"Container '{container_name}' successfully deleted!"}), 200

    except ItemNotFound as e:
        return jsonify ({'error': f"{e.message}"}), 404
    except pymongo.errors.ConnectionFailure as e:
        return jsonify({'error': 'Connection to database failed.'}), 500
    except docker.errors.NotFound:
        return jsonify({'Container not found': f'{container_name}'}), 404
    except Exception as e:
        return jsonify ({'error': f"{e}"})
    
     
@app.route('/container/list', methods=['GET'])
def read_container():
 
    try:
        containerlist = list(containerCollection.find({} ,{"_id": 0}))
        return jsonify(containerlist), 200
       
    except pymongo.errors.ConnectionFailure as e:
        return jsonify({'error': 'Connection to database failed.'}), 500
    except Exception as e:
        return jsonify({"error": f"Error in reading container list. {e}"}), 500
    

#get container by service -returns the top priority container with the specified service
@app.route('/container/<service_port>', methods=['GET'])
def get_container_by_service(service_port):

    try:
        validated_data = ServicePortSchema().load({"service_port":service_port})
    except ValidationError as e:
        return jsonify({"error": f"{e}"}), 400

    try:
        container = search_container_by_service (service_port, containerCollection)
        print(container)
        if container:        
            container[0].pop("_id",None)
            return jsonify(container[0]), 200
        return jsonify ({}), 200
    except pymongo.errors.ConnectionFailure as e:
        return jsonify({'error': 'Connection to database failed.'}), 500
    except Exception as e:
        return jsonify({"error": f"Error in reading container list. {e}"}), 500
    

@app.route('/container/start/<container_name>', methods=['POST'])
def start_container(container_name):
  
    try:
        validated_data = ContainerNameSchema().load({"container_name":container_name})
    except ValidationError as e:
        return jsonify({"error": f"{e}"}), 400

    try:
        #Check if container exists
        if not check_if_value_field_exists("name", container_name, containerCollection):
            return jsonify({'error': f"Container name {container_name} doesn't exists."})
 
        container = client.containers.get(container_name)
        container.start()

        #refresh status
        container = client.containers.get(container_name)
        update_item_list (container_name, "status", container.status, containerCollection)
        return jsonify({'Container started successfully.': f'{container_name}'}), 200
    
    except (ContainerNotFound, docker.errors.NotFound) as e:
        return jsonify ({'error': f'Container {container_name} not found'}), 404
    except ItemNotModified as e:
        return jsonify ({'message': f"{e.message}"}), 200
    except pymongo.errors.ConnectionFailure as e:
        return jsonify({'error': 'Connection to database failed.'}), 500
    except Exception as e:
        return jsonify({"error": f"Error in reading container list. {e}"}), 500

    

@app.route('/container/stop/<container_name>', methods=['POST'])
def stop_container(container_name):
     
    try:
        validated_data = ContainerNameSchema().load({"container_name":container_name})
    except ValidationError as e:
        return jsonify({"error": f"{e}"}), 400
         
    try:
        #Check if container exists
        if not check_if_value_field_exists("name", container_name, containerCollection):
            return jsonify({'error': f"Container name {container_name} doesn't exists."})

        container = client.containers.get(container_name)
        container.stop()
        
        #refresh status
        container = client.containers.get(container_name)
        update_item_list (container_name, "status", container.status, containerCollection)
        return jsonify({'Container started successfully.': f'{container_name}'}), 200
    
    except (ContainerNotFound, docker.errors.NotFound) as e:
        return jsonify ({'error': f'Container {container_name} not found'}), 404
    except ItemNotModified as e:
        return jsonify ({'message': f"{e.message}"}), 200
    except pymongo.errors.ConnectionFailure as e:
        return jsonify({'error': 'Connection to database failed.'}), 500
    except Exception as e:
        return jsonify({"error": f"Error in reading container list. {e}"}), 500
    

#returns the number of containers in each vm 
@app.route('/container/count', methods=['GET'])
def container_number():
    try:
        result = count_container(containerCollection)
        result_dict = {item["vm_name"]: item["number_of_containers"] for item in result}

        return jsonify(result_dict), 200

    except Exception as e:
        return jsonify({"error": f"Error in reading container list. {e}"}), 500
    

@app.route('/container/ping', methods=['GET'])
def ping():
    return jsonify("server running"), 200

    
if __name__ == '__main__':
    app.run(host=app.config['IP_ADDRESS'], port=app.config['PORT'])
