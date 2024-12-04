from functions import *
from exceptions import *
from config import DevelopmentConfig
from flask import Flask, jsonify, request, send_from_directory
import requests
import json
from flask_swagger_ui import get_swaggerui_blueprint


app = Flask (__name__)
app.config.from_object(DevelopmentConfig)  # Load the configuration

#Server Address for vm configuration 
VM_SERVER_URL=f"http://{app.config['VM_SERVER_IP']}:{app.config['VM_SERVER_PORT']}"

#Port for container configuration
CONTAINER_SERVER_PORT=app.config['CONTAINER_SERVER_PORT']

MAX_CONTAINERS=app.config['MAX_CONTAINERS']

# Init
try:
    #Obtain services list
    services_list = get_services_list(VM_SERVER_URL)
    print (services_list)

    #Obtain vm list
    # vms_list = get_vm_list(VM_SERVER, PORT_CONTAINER_SERVER)
    # print (vms_list)
    vms_list= {'vms': []}
    print (vms_list)
    
    #Obtain honeyfarm list
    
    HoneyfarmList = {
    "ssh": [
      {
        "container_name": "corwrie",
        "ip": "10.10.10.11",
        "port": "4442",
        "rtt": "10ms",
        "status": "running",
        "busy":"True"
      },
      {
        "container_name": "corwrie",
        "ip": "10.10.10.10",
        "port": "4444",
        "rtt": "10ms",
        "status": "exited",
        "busy":"True"

      },
      {
        "container_name": "corwrie",
        "ip": "10.10.10.10",
        "port": "4445",
        "rtt": "10ms",
        "status": "running",
        "busy":"True"

      }
    ],
    "telnet": []
    }
    print (HoneyfarmList)
    

except ServiceListError as e:
    print (f"Error: {e.message}")
except VmListError as e:
    print (f"Error: {e.message}")
except VMServerNotRunning as e:
    print (f"Error: {e.message}")
except ContainerServerNotRunning as e:
    print (f"Error: {e.message}")
except Exception as e:
    print (f"Error: {e}")




#WEBHOOKS for vm and container updates

@app.route('/tinmanager/vmwebhook', methods=['POST'])
def vm_webhook():
    data = request.json
    print (data)
    


@app.route('/tinmanager/containerwebhook', methods=['POST'])
def container_webhook():
    data = request.json
    print(data)







@app.route('/tinmanager/addflow', methods=['POST'])
def add_flow():
    data = request.json
    src_ip = data.get('src_ip')
    dst_ip = data.get('dst_ip')
    port = data.get('port')
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
    

    #Association service -> port
    service = services_list.get(port)
    if (service == None): 
        service="default"
    print ("service: ",service)

    try:

        honeypot=get_available_container(service,HoneyfarmList)
        
        if (not honeypot):
            honeyfarm=get_available_vm(vms_list,MAX_CONTAINERS)

            if (not honeyfarm):
                print ("VM not found. Creating vm..")
                honeyfarm=create_vm(VM_SERVER_URL)          
                     
            print("chosen vm:", honeyfarm["ip"])

            honeypot=create_container(honeyfarm["ip"],image) #image devo sceglierla in base al servizio 
        
        print ("chosen honeypot: ",honeypot["ip"],honeypot["port"])

        #create_flow(....,honeypot["ip"],"honeypot["port"]")

        return jsonify({"message":  "Flow successfully created!"}), 201
    
    except Exception as e:
        return jsonify({'error': f'Error {e}'}), 500

 


    #cerca associazione porta -> servizio nella lista services OK
    #leggi items in lista containers corrispondente al servizi OK
        #se lista vuota -> vai a creazione OK
        #se lista piena->controlla busy OK
            #se tutti busy -> vai a creazione OK
            #se qualcuno free -> controlla status OK
                #se status sus -> risolvi o crea OK
                #se running -> scegli container OK
    
    #creazione:
    #cerca vm nella lista vm con occupied_slot < MAX
        #se non c'è ->crea vm (richiesta a container_configurator) OK
        #se c'è-> creo container su container_configurator con l'ip della vm OK

    #faccio flow

# {
    #   "honeyfarm": [
    #     {
    #       "ssh": [
    #         {
    #           "container_name": "corwrie",
    #           "ip": "10.10.10.10",
    #           "port": "4444",
    #           "rtt": "10ms",
    #           "status":"running"
    #           "busy":True
    #         },
    #         {
    #           "container_name": "corwrie",
    #           "ip": "10.10.10.11",
    #           "port": "4444",
    #           "rtt": "10ms",
    #           "status": "occupied"
    #         }
    #       ]
    #     },
    #     {
    #       "telnet": []
    #     }
    #   ]
    # }










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
    app.run(port=5003)