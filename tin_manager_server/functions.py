from time import sleep
from exceptions import *
from flask import Flask, jsonify, request, send_from_directory
import requests
import json



def get_services_list(VM_SERVER):

    if server_running(VM_SERVER, "vm"):
        url= f"{VM_SERVER}/vm/list_honeypot_services"
        response=requests.get(url)
        if (response.status_code == 200):
            services = response.json()
        else:
            raise ServiceListError ("Service list not obtained.", error_code=response.status_code)
    
    return services


def get_vm_list (VM_SERVER, PORT_CONTAINER_SERVER):

    vms_list = {"vms": []}

    #Request to vm_configurator
    if server_running(VM_SERVER, "vm"):
        url= f"{VM_SERVER}/vm/list"
        response=requests.get(url)
        if (response.status_code == 200):
            server_vms_list = response.json()
        else:
            raise VmListError ("Vm list not obtained.", error_code=response.status_code)
        
    for vm in server_vms_list.get("vms", []):
            ip = vm.get("ip")
            
            #Request to container_configurator
            CONTAINER_SERVER = f"http://{ip}:{PORT_CONTAINER_SERVER}" 
            if server_running(CONTAINER_SERVER, "container"):
                url = f"{CONTAINER_SERVER}/container/count"
                response = requests.get(url)
                if (response.status_code == 200):
                    n_container = response.json()
                else:
                    raise VmListError ("Vm list not obtained.", error_code=response.status_code)
        
            # Add information to vm_list
            new_vm_entry = {
                "name": vm.get("name"),
                "ip": vm.get("ip"),
                "status": vm.get("status"),
                "n_container": n_container
            }
            vms_list["vms"].append(new_vm_entry)
        
    return vms_list


def get_honeyfarm_list (VM_SERVER, PORT_CONTAINER_SERVER):
    HoneyfarmList={
        "honeyfarm": [
        ]
    }

    #[TODO] Ottenere il json:
    # {
    #   "containers": [
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

    #Opzione 1: chiedere al vm configurator la lista degli ip per poi fare le richieste ai container cnfigurator per le info
    #Opzione 2: prendere gli ip dalla lista delle vm che ha già il tin manager
        


    



#Check if vm_configurator is running
def server_running (SERVER, path):
    while (True):
        try:
            url= f"{SERVER}/{path}/ping"
            response=requests.get(url)
            if (response.status_code == 200):
                return True     
        except requests.exceptions.ConnectionError as e:
            print("Server not found. Check if it's running and if the configured IP and Ports are correct.\n")
        except Exception as e:
            return False
        sleep(5)