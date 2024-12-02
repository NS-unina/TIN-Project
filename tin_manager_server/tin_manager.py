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
VM_SERVER=app.config['VM_SERVER']

#Port for container configuration
PORT_CONTAINER_SERVER=app.config['PORT_CONTAINER_SERVER']


# Init
try:
    #Obtain services list
    services_list = get_services_list(VM_SERVER)
    print (services_list)

    #Obtain vm list
    vms_list = get_vm_list(VM_SERVER, PORT_CONTAINER_SERVER)
    print (vms_list)

    #Obtain honeyfarm list
    HoneyfarmList = get_honeyfarm_list()

except ServiceListError as e:
    print (e.message)
except VmListError as e:
    print (e.message)





#WEBHOOKS for vm and container updates (?) VS POLLING

@app.route('/tinmanager/vmwebhook', methods=['POST'])
def vm_webhook():
    data = request.json
    


@app.route('/tinmanager/containerwebhook', methods=['POST'])
def container_webhook():
    data = request.json
    







@app.route('/tinmanager/addflow', methods=['POST'])
def add_flow():
    data = request.json
    src_ip = data.get('src_ip')
    dst_ip = data.get('dst_ip')
    port = data.get('port')
    ovs_id=data.get('ovs_id')

    #check fields
    if not src_ip:
        return jsonify({"error": "src_ip field is needed"}), 400
    if not dst_ip:
        return jsonify({"error": "dst_ip field is needed"}), 400
    if not port:
        return jsonify({"error": "port field is needed"}), 400
    if not ovs_id:
        return jsonify({"error": "ovs_id field is needed"}), 400


    
    service = services_list.get(port)
    if (service == None): 
        #ritorna errore servizio non supportato ? o magari buttiamo su una honeypot di default?
        service="default"

    for service in HoneyfarmList["honeyfarm"]:
        for container in service.get("ssh",[]):
            print(container)
            if (not container):
                #chiama create container
                #create_container()
                print("creating container")
            else:
                print("checking container status")
                





    
     
    





    #cerca associazione porta -> servizio nella lista services
    #leggi items in lista containers corrispondente al servizio
        #se lista vuota -> vai a creazione
        #se lista piena->controlla busy
            #se tutti busy -> vai a creazione
            #se qualcuno free -> controlla status
                #se status sus -> risolvi o crea
                #se running -> scegli container
    
    #creazione:
    #cerca vm nella lista vm con occupied_slot < MAX
        #se non c'è ->crea vm (richiesta a container_configurator)
        #se c'è-> creo container su container_configurator con l'ip della vm

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