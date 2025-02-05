from functions import *
from exceptions import *
from validation_schemas import *
from config import DevelopmentConfig
from flask import Flask, jsonify, request, send_from_directory
import requests
import json

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

#from flask_swagger_ui import get_swaggerui_blueprint



# ********[ LOAD CONFIGURATION FROM config.py ]********
app = Flask (__name__)
app.config.from_object(DevelopmentConfig)  # Load the configuration

#Server Address for vm configuration 
VM_SERVER_URL=f"http://{app.config['VM_SERVER_IP']}:{app.config['VM_SERVER_PORT']}"

#Port for container configuration
CONTAINER_SERVER_PORT=app.config['CONTAINER_SERVER_PORT']

MAX_CONTAINERS=app.config['MAX_CONTAINERS']
UTILIZATION_LIMIT=app.config['UTILIZATION_LIMIT']

#Server Address for vm configuration 
ONOS_URL=f"http://{app.config['ONOS_IP']}:{app.config['ONOS_PORT']}"
ONOS_AUTH_USERNAME = app.config['ONOS_AUTH_USERNAME']
ONOS_AUTH_PASSWORD = app.config['ONOS_AUTH_PASSWORD']


#Startup check

while True:
    try:
        print ("Attempting to connect to vm configurator...")
        vmList = get_vm_list(VM_SERVER_URL)
        print(vmList)
        if not vmList:
            print ("No available vms.")
            create_vm(VM_SERVER_URL)

        for vm in vmList:
            if vm["status"] == "running":                               #[FIXME] e se la vm è accesa ma container configurator non è running?
                IP_CONTAINER_MASTER = vm["ip"]
                print ("Container Master: ",IP_CONTAINER_MASTER)
                break

        print ("\nSTARTUP DONE")
        break
    
    except ServerNotRunning as e:
        print("[ERROR] Connection to vm configurator failed. Retrying...")
        sleep(7)
    except Exception as e:
        print(jsonify({"error": f"{str(e)}"}))
        break


# Configuration of BackgroundScheduler
scheduler = BackgroundScheduler()
scheduler.start()

#[TODO] gestione errore connessione onos
#scheduler.add_job(lambda: flow_cleanup(ONOS_URL, ONOS_AUTH_USERNAME, ONOS_AUTH_PASSWORD, CONTAINER_SERVER_PORT), trigger=IntervalTrigger(seconds=30))
scheduler.add_job(lambda: vm_manager(IP_CONTAINER_MASTER, CONTAINER_SERVER_PORT, VM_SERVER_URL, MAX_CONTAINERS, UTILIZATION_LIMIT), trigger=IntervalTrigger(seconds=10))




# ********[ API ]********
@app.route('/tinmanager/tcp/addflow', methods=['POST'])
def add_flow():
    data = request.json

    try:
        validated_data = AddFlowSchema().load(data)
    except ValidationError as e:
        return jsonify({"error": f"{e}"}), 400

    src_ip = data.get('src_ip')
    dst_ip = data.get('dst_ip')
    src_port = data.get('src_port')
    dst_port = data.get('dst_port')
    ovs_id=data.get('ovs_id')

    
    try:
        #Get vmList
        vmList = get_vm_list(VM_SERVER_URL)
        print(vmList)
        if not vmList:
            print ("No available vms.")
            create_vm(VM_SERVER_URL)

        #Select container master (first vm that is running)
        for vm in vmList:
            if vm["status"] == "running":                               #[FIXME] e se la vm è accesa ma container configurator non è running?
                ip_container_master = vm["ip"]
                break
        #[TODO] ACCENDI UNA VM spenta se ho vm list ma non ho ipcontainer master

        #Get containerList by service_port
        container = get_container_by_service (f"http://{ip_container_master}:{CONTAINER_SERVER_PORT}", dst_port)
        print (container)
        
        if not container :
           
            #Find if there is a vm available on which to create the container
            print (f"Requesting number of container on each vm ...")
            containerCount = get_container_count(f"http://{ip_container_master}:{CONTAINER_SERVER_PORT}")
            print (containerCount)

            chosen_vm = choose_vm (vmList, containerCount, MAX_CONTAINERS)
            if (not chosen_vm):
                print ("No available vm found. Creating vm ...")
                #chosen_vm=create_vm(VM_SERVER_URL)
            print("Chosen vm: ", chosen_vm)

            #Creating container 
            print ("Creating container ...")
            #container = create_container(chosen_vm["ip"],CONTAINER_SERVER_PORT,dst_port)


        #Set flow ip and port with the found container
        vm_ip_mac= get_vm_ip_mac_by_name (container["vm_name"], vmList)
        flow_ip=vm_ip_mac["ip"]
        flow_mac=vm_ip_mac["mac"]
        for service in container["services"]:
            if(service["service_port"]==dst_port):
                flow_port=service["vm_port"]
        
        #Creating flow
        print (f"Creating tcp flow: ip '{flow_ip}', port '{flow_port}', mac '{flow_mac}'")
        #create_flow_tcp(ONOS_URL, ONOS_AUTH_USERNAME, ONOS_AUTH_PASSWORD, ovs_id, src_ip, dst_ip, dst_port, container_ip, container_mac,container_vm_port)

        return jsonify({"message":  "Flow successfully created!"}), 201
    
    except (VmListError, ContainerListError) as e:
        return jsonify({'error': f'{e.message}'}), 500
    except (CreateFlowFailed, CreateVmFailed, CreateContainerFailed) as e:
        return jsonify({'error': f'{e.message}'}), 500
    except requests.exceptions.ConnectionError as e:
        return jsonify({'error': f'{e}'}), 500
    except Exception as e:
        return jsonify({'error': f'{e}'}), 500




@app.route('/tinmanager/containerlimit', methods=['POST'])
def containerLimit():
    global MAX_CONTAINERS

    data = request.json
    try:
        validated_data = MAX_CONTAINERSSchema().load(data)
    except ValidationError as e:
        return jsonify({"error": f"{e}"}), 400

    try:               
        MAX_CONTAINERS = data.get('max_containers')
        return jsonify(f"Max num container modified to {MAX_CONTAINERS}."), 200
    
    except Exception as e:
        return jsonify({'error': f'{e}'}), 500


@app.route('/tinmanager/ping', methods=['GET'])
def ping():
    return jsonify("server running"), 200





#Swagger docs api
# SWAGGER_URL = '/apidocs'
# API_DOCS_PATH = 'tinmanager_docs.json'

# swagger_ui_blueprint = get_swaggerui_blueprint(
#     SWAGGER_URL,
#     f'/{API_DOCS_PATH}',
#     config={
#         'app_name': "TIN Manager API Documentation"
#     }
# )
# app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)


#Request for documentation
# @app.route(f'/{API_DOCS_PATH}')
# def serve_swagger_file():
#     return send_from_directory('.', API_DOCS_PATH)

if __name__ == '__main__':
    app.run(host=app.config['IP_ADDRESS'], port=app.config['PORT'])
