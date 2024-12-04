from time import sleep
from exceptions import *
from flask import Flask, jsonify, request, send_from_directory
import requests
import json



def get_services_list(VM_SERVER_URL):

    try:
        url= f"{VM_SERVER_URL}/vm/services"
        response=requests.get(url)
        if (response.status_code == 200):
            services = response.json()
            return services
        else:
            raise ServiceListError ("Service list not obtained.", error_code=response.status_code)
    except requests.exceptions.ConnectionError:
        raise VMServerNotRunning ("VM Server not running. Can not configure services list.", error_code=503)


def get_vm_list (VM_SERVER_URL, CONTAINER_SERVER_PORT):

    vms_list = {"vms": []}
    
    try:
        #Request to vm_configurator
        url= f"{VM_SERVER_URL}/vm/list"
        response=requests.get(url)
        if (response.status_code == 200):
            server_vms_list = response.json()
        else:
            raise VmListError ("Vm list not obtained.", error_code=response.status_code)
    except requests.exceptions.ConnectionError:
        raise VMServerNotRunning ("VM Server not running. Can not configure vms list.", error_code=503)
    

    for vm in server_vms_list.get("vms", []):
            ip = vm.get("ip")
            
            # try:
                # #Request to container_configurator
                # CONTAINER_SERVER = f"http://{ip}:{CONTAINER_SERVER_PORT}" 
                # url = f"{CONTAINER_SERVER}/container/count"
                # response = requests.get(url)
                # if (response.status_code == 200):
                #     n_container = response.json()
                # else:
                #     raise VmListError ("Vm list not obtained.", error_code=response.status_code)
            # except requests.exceptions.ConnectionError:
            #     raise ContainerServerNotRunning ("Container Server not running. Can not configure contaniers list.", error_code=503)

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


def get_honeyfarm_list (VM_SERVER, CONTAINER_SERVER_PORT):
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
        


#Find available container
def get_available_container(service,HoneyfarmList):

    existing_containers= HoneyfarmList.get(service)
    if (not existing_containers):
        return 
                 
    for container in existing_containers:
        print("--------------------")   
        print("checking if container is busy")
        print(container["busy"])
        
        if(container["busy"]=="False"):
            print("checking status")
            if (container["status"]=="running"):
                 print("Container found",container)
                 return container
            else:
                 #container not running
                 print(container["status"])
                 continue

    #If no one is available
    return 


def get_available_vm(vms_list,MAX_CONTAINERS):
     
    print(vms_list)
    #{'vms': [{'name': 'test2', 'ip': '127.0.0.1', 'status': 'not_created', 'n_container': '3'}]}

    if (not vms_list):
        return

    for vm in vms_list["vms"]:
        print (vm["ip"])        
        #check capacity
        if(int(vm["n_container"]) >= MAX_CONTAINERS):
              print("Max containers reached for vm: ",vm["name"])
              continue 
        else:
              #check status
              if (vm["status"]=="running"):
                   print("vm found:", vm["name"],vm["status"])
                   return vm  
    return 



def create_container(vm_ip,vm_port,image): 

    url= f"http://{vm_ip}:{vm_port}/container/create"
    
    payload=json.dumps({"image":f"{image}"})
    response=requests.post(url,json=payload)
    if (response.status_code == 201):
        print("Container created successfully!")
        print(response.json()["container"])
        
        return response.json()["container"]
    else:
        raise CreateContainerFailed (f"{response.json}", error_code=response.status_code)


def create_vm(VM_SERVER_URL):

    url= f"{VM_SERVER_URL}/vm/create"
    print (url)
    
    #payload=json.dumps({"":f"{}"})
    response=requests.post(url,json={}) #per ora manda vuoto quindi usa tutti i valori di default
    if (response.status_code == 201):
        print("Vm created successfully!")
        return response.json()["vm"]
    else:
        raise CreateContainerFailed (f"{response.json}", error_code=response.status_code)

