from functions import *
from exceptions import *
from config import DevelopmentConfig
from flask import Flask, jsonify, request, send_from_directory
import requests
import json

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from flask_swagger_ui import get_swaggerui_blueprint



# ********[ LOAD CONFIGURATION FROM config.py ]********
app = Flask (__name__)
app.config.from_object(DevelopmentConfig)  # Load the configuration

#Server Address for vm configuration 
VM_SERVER_URL=f"http://{app.config['VM_SERVER_IP']}:{app.config['VM_SERVER_PORT']}"

#Port for container configuration
CONTAINER_SERVER_PORT=app.config['CONTAINER_SERVER_PORT']

MAX_CONTAINERS=app.config['MAX_CONTAINERS']

#Server Address for vm configuration 
ONOS_URL=f"http://{app.config['ONOS_IP']}:{app.config['ONOS_PORT']}"
ONOS_AUTH_USERNAME = app.config['ONOS_AUTH_USERNAME']
ONOS_AUTH_PASSWORD = app.config['ONOS_AUTH_PASSWORD']


# Configuration of BackgroundScheduler
scheduler = BackgroundScheduler()
scheduler.start()
scheduler.add_job(lambda: flow_cleanup(ONOS_URL, ONOS_AUTH_USERNAME, ONOS_AUTH_PASSWORD, CONTAINER_SERVER_PORT), trigger=IntervalTrigger(seconds=15))


# ********[ API ]********
@app.route('/tinmanager/testflow', methods=['POST'])
def test_flow():

    data = request.json
    src_ip = data.get('src_ip')
    dst_ip = data.get('dst_ip')
    src_port = data.get('src_port')
    dst_port = data.get('dst_port')
    ovs_id=data.get('ovs_id')


    payload= {
        "flows": [
            {
                "priority": 50000,
                "timeout": 0,
                "isPermanent":"true",
                "deviceId": f"{ovs_id}",
                "treatment": {
                    "instructions": [
                        {
                            "type": "OUTPUT",
                            "port": "NORMAL"
                        }
                    ]
                },
                "selector": {
                    "criteria": [
                        {
                            "type": "ETH_TYPE",
                            "ethType": "0x0800"
                        },
                        {
                            "type": "IPV4_SRC",
                            "ip": f"{src_ip}/32"
                        },
                        {
                            "type": "IPV4_DST",
                            "ip": f"{dst_ip}/32"
                        }
                       
                    ]
                }
            }
        ]
    }



    username = "onos"
    password = "rocks"


    url= "http://localhost:8181/onos/v1/flows"
    response=requests.post(url,json=payload,auth=(username, password))
    print (response.json())
    
    return jsonify({"message":  "Flow successfully created!"}), 201















# ********[ API ]********
@app.route('/tinmanager/addflow', methods=['POST'])
def add_flow():
    data = request.json
    src_ip = data.get('src_ip')
    dst_ip = data.get('dst_ip')
    src_port = data.get('src_port')
    dst_port = data.get('dst_port')
    ovs_id=data.get('ovs_id')

    #check fields
    # if not src_ip:
    #     return jsonify({"error": "src_ip field is needed"}), 400
    # if not dst_ip:
    #     return jsonify({"error": "dst_ip field is needed"}), 400
    # if not port:
    #     return jsonify({"error": "port field is needed"}), 400
    # if not ovs_id:
    #     return jsonify({"error": "ovs_id field is needed"}), 400
    


    try:
        #Get vmList
        vmList = get_vm_list(VM_SERVER_URL)
        print(vmList)

        #Get containerList by service_port
        if not vmList:
            print ("No available vms.")

        for vm in vmList:
            if vm["status"] == "running":
                ip_container_master = vm["ip"]
                break

        #[TODO] ACCENDI UNA VM spenta


        print (f"Requesting available container list from {ip_container_master}:{CONTAINER_SERVER_PORT} ...")
        container = get_container_by_service (f"http://{ip_container_master}:{CONTAINER_SERVER_PORT}", dst_port)
        print (container)
        
        
        #Check if there is a honeypot available
        if  not container :
           
            #Find if there is a vm available on which to create the container
            print (f"Requesting number of container on each vm from {ip_container_master}:{CONTAINER_SERVER_PORT} ...")
            containerCount = get_container_count(f"http://{ip_container_master}:{CONTAINER_SERVER_PORT}")
            print (containerCount)

            chosen_vm=None
            for vm in vmList:
                if containerCount and (containerCount[vm["name"]] >= MAX_CONTAINERS):
                        print("vm is full: ",vm["name"])
                        continue
                elif(vm["status"]!="running") : 
                    continue
                else:
                    print("chosen vm: ",vm["name"])
                    chosen_vm=vm
                    break

            if (not chosen_vm):
                print ("no available vm found, creating vm")
                #chosen_vm=create_vm(VM_SERVER_URL)

               
            print ("Creating container...")
            container = create_container(chosen_vm["ip"],CONTAINER_SERVER_PORT,dst_port)


        #Set flow ip and port with the found container
        vm_ip_mac= get_vm_ip_mac_by_name (container["vm_name"], vmList)
        flow_ip=vm_ip_mac["ip"]
        flow_mac=vm_ip_mac["mac"]
        for service in container["services"]:
            if(service["service_port"]==dst_port):
                flow_port=service["vm_port"]
        
        #Creating flow
        print (f"Creating flow: ip '{flow_ip}', port '{flow_port}', mac '{flow_mac}'")
        #create_flow(....,flow_ip,flow_port)

        return jsonify({"message":  "Flow successfully created!"}), 201
    
    except (VmListError, ContainerListError) as e:
        return jsonify({'error': f'{e.message}'}), 500
    except ServerNotRunning as e:
        return jsonify({'error': f'{e.message}'}), 500
    except CreateContainerFailed as e:
        return jsonify({'error': f'{e.message}'}), 500
















    # try:

    #     honeypot=get_available_container(service,HoneyfarmList)
        
    #     if (not honeypot):
    #         honeyfarm=get_available_vm(vms_list,MAX_CONTAINERS)

    #         if (not honeyfarm):
    #             print ("VM not found. Creating vm..")
    #             honeyfarm=create_vm(VM_SERVER_URL)          
                     
    #         print("chosen vm:", honeyfarm["ip"])

    #         honeypot=create_container(honeyfarm["ip"],image) #image devo sceglierla in base al servizio 
        
    #     print ("chosen honeypot: ",honeypot["ip"],honeypot["port"])

    #     #create_flow(....,honeypot["ip"],"honeypot["port"]")

    #     return jsonify({"message":  "Flow successfully created!"}), 201
    
    # except Exception as e:
    #     return jsonify({'error': f'Error {e}'}), 500

 



@app.route('/tinmanager/ping', methods=['GET'])
def ping():
    return jsonify("server running"), 200























#Swagger docs api
SWAGGER_URL = '/apidocs'
API_DOCS_PATH = 'tinmanager_docs.json'

swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    f'/{API_DOCS_PATH}',
    config={
        'app_name': "TIN Manager API Documentation"
    }
)
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)

#Request for documentation
@app.route(f'/{API_DOCS_PATH}')
def serve_swagger_file():
    return send_from_directory('.', API_DOCS_PATH)

if __name__ == '__main__':
    app.run(host=app.config['IP_ADDRESS'], port=app.config['PORT'])
