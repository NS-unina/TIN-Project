from functions import *
from exceptions import *
from config import DevelopmentConfig
from flask import Flask, jsonify, request, send_from_directory
import requests
import json
from flask_swagger_ui import get_swaggerui_blueprint


# ********[ LOAD CONFIGURATION FROM config.py ]********
app = Flask (__name__)
app.config.from_object(DevelopmentConfig)  # Load the configuration

#Server Address for vm configuration 
VM_SERVER_URL=f"http://{app.config['VM_SERVER_IP']}:{app.config['VM_SERVER_PORT']}"

#Port for container configuration
CONTAINER_SERVER_PORT=app.config['CONTAINER_SERVER_PORT']

MAX_CONTAINERS=app.config['MAX_CONTAINERS']





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
        ip_container_master = vmList[0]["ip"]
        print (ip_container_master)
        containerList = get_container_list_by_service (f"http://{ip_container_master}:{CONTAINER_SERVER_PORT}", dst_port)
        print (containerList)

        #Check if there is a honeypot available
        if containerList and containerList["services"]["busy"] == "False":
            print("found free container")
            flow_port = containerList["services"]["vm_port"] 
            flow_ip = get_vm_ip_by_name (containerList["vm_name"], vmList)

            print ("flow ip and port: ",flow_ip,flow_port)
        else:
            #Find if there is available vm
            print ("Get container count")
            containerCount = get_container_count(f"http://{ip_container_master}:{CONTAINER_SERVER_PORT}")
            print (containerCount)
            chosen_vm=None
            for vm in containerCount:
                if (containerCount[vm]<MAX_CONTAINERS):
                    print("found vm")
                    for item in vmList:
                        if (item["name"]==vm):
                            chosen_vm=item
                            print("chosen vm:",chosen_vm)
                            break
                    break          
            if (not chosen_vm):
                print ("creating vm")
                #chosen_vm=create_vm(VM_SERVER_URL)
            
            print (chosen_vm)
            #new_container=create_container(chosen_vm["ip"], vm_port?,dst_port )
            #flow_port = new_container["services"]["vm_port"] 
            #flow_ip = chosen_vm["ip"]


                    
            #print ("chosen honeypot: ",honeypot["ip"],honeypot["port"])

            #create_flow(....,flow_ip,flow_port)

        return jsonify({"message":  "Flow successfully created!"}), 201
    except (VmListError, ContainerListError) as e:
        return jsonify({'error': f'{e.message}'}), 500
    except ServerNotRunning as e:
        return jsonify({'error': f'{e.message}'}), 500



        
        #if non trovato 
        #
        #   ottieni la lista di vmList -> /vm/list
        #   ottieni n container per vm -> /container/count , se disponibile memorizza ip

        #   if not vm disponibile
        #     crea_vm -> /vm/create (memorizzati l'ip della vm)
        #   
        #   crea container -> /container/create (passare service_port, ti deve prendere porta flow)  -    
        # 
        #      
    













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
    app.run(host=app.config['IP_ADDRESS'], port=app.config['PORT'])
