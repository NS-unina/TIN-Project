from time import sleep
from exceptions import *
from flask import Flask, jsonify, request, send_from_directory
import requests
import json



def get_services_list(VM_SERVER):

    #if server_running(VM_SERVER, "vm"):
    url= f"{VM_SERVER}/vm/services"
    response=requests.get(url)
    if (response.status_code == 200):
        services = response.json()
        return services
    else:
        raise ServiceListError ("Service list not obtained.", error_code=response.status_code)
    
    # else:
    #     return ("error ")#mettere l'exception
    


def get_vm_list (VM_SERVER, PORT_CONTAINER_SERVER):

    vms_list = {"vms": []}

    #Request to vm_configurator
    #if server_running(VM_SERVER, "vm"):
    url= f"{VM_SERVER}/vm/list"
    response=requests.get(url)
    if (response.status_code == 200):
        server_vms_list = response.json()
    else:
        raise VmListError ("Vm list not obtained.", error_code=response.status_code)
        
    for vm in server_vms_list.get("vms", []):
            ip = vm.get("ip")
            
            # #Request to container_configurator
            # CONTAINER_SERVER = f"http://{ip}:{PORT_CONTAINER_SERVER}" 
            # #if server_running(CONTAINER_SERVER, "container"):
            # url = f"{CONTAINER_SERVER}/container/count"
            # response = requests.get(url)
            # if (response.status_code == 200):
            #     n_container = response.json()
            # else:
            #     raise VmListError ("Vm list not obtained.", error_code=response.status_code)
        
            # Add information to vm_list
            new_vm_entry = {
                "name": vm.get("name"),
                "ip": vm.get("ip"),
                "status": vm.get("status"),
                "n_container": "3" #n_container
            }
            ##########
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
        


#find available container
def get_available_container(service,HoneyfarmList):

    existing_containers= HoneyfarmList.get(service)
    if (not existing_containers):
            print("no available container found")
            return #eccezione o false o none?
            
    else:        
            for container in existing_containers:
                print("--------------------")   
                print("checking if container is busy")
                print(container["busy"])
                if(container["busy"]=="False"):
                     #controllo status del container libero
                     print("checking status")
                     if (container["status"]=="running"):
                          #trovato container
                          print("container found",container)
                          return container
                     else:
                          #container non running
                          print(container["status"])
                          continue
                else: continue

            #qua entro se trovo tutti occupati
            print("no available container found")
            return 


def get_available_vm(vms_list,MAX_CONTAINERS):
     
     print(vms_list)

     return

def create_container():
     
     return
    



#Check if vm_configurator is running
def server_running (SERVER, path):
    while (True):
        try:
            url= f"{SERVER}/{path}/ping"
            response=requests.get(url)
            if (response.status_code == 200):
                print("server found")
                return True      
        except requests.exceptions.ConnectionError as e:
            print("Server not found. Check if it's running and if the configured IP and Ports are correct.\n")
        except Exception as e:
            return False
        sleep(5)