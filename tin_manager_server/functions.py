from time import sleep
from exceptions import *
from flask import Flask, jsonify, request, send_from_directory
import requests
import json



def get_vm_list (VM_SERVER_URL):
 
  try:
      #Request to vm_configurator
      url= f"{VM_SERVER_URL}/vm/list"
      response=requests.get(url)
      if (response.status_code == 200):
          vms_list = response.json()
          return vms_list
      else:
          raise VmListError ("Vm list not obtained.", error_code=response.status_code)
  except requests.exceptions.ConnectionError:
      raise ServerNotRunning ("VM Server not running. Can not configure vms list.", error_code=503)
  

def get_container_list_by_service (CONTAINER_SERVER_URL, service_port):
 
  try:
      #Request to vm_configurator
      url= f"{CONTAINER_SERVER_URL}/container/{service_port}"
      response=requests.get(url)
      if (response.status_code == 200):
          containerList = response.json()
          return containerList
      else:
          raise ContainerListError ("Container list not obtained.", error_code=response.status_code)
  except requests.exceptions.ConnectionError:
      raise ServerNotRunning ("Container Server not running. Can not configure container list.", error_code=503)


def get_vm_ip_by_name (vm_name, vmList):
    for vm in vmList:
        if vm["name"] == vm_name:
            return vm["ip"]
    

def get_container_count(CONTAINER_SERVER_URL):
  try:
      #Request to vm_configurator
      url= f"{CONTAINER_SERVER_URL}/container/count"
      response=requests.get(url)
      if (response.status_code == 200):
          containerCount = response.json()
          return containerCount
      else:
          raise ContainerListError ("Container count not obtained.", error_code=response.status_code)
  except requests.exceptions.ConnectionError:
      raise ServerNotRunning ("Container Server not running. Can not configure container list.", error_code=503)











def create_vm(VM_SERVER_URL):
  try:
    url= f"{VM_SERVER_URL}/vm/create"
 
    response=requests.post(url,json={}) #default values
    if (response.status_code == 201):
        print("Vm created successfully!")
        return response.json()["vm"]
    else:
      raise CreateVmFailed (f"{response.json}", error_code=response.status_code)
    
  except requests.exceptions.ConnectionError:
    raise ServerNotRunning ("VM Server not running. Can not configure vms list.", error_code=503)



def create_container(vm_ip,vm_port,service_port): 

    url= f"http://{vm_ip}:{vm_port}/container/create"
    
    payload=json.dumps({"service_port":f"{service_port}"})
    response=requests.post(url,json=payload)
    if (response.status_code == 201):
        print("Container created successfully!")
        print(response.json()["container"])
        return response.json()["container"]
    else:
        raise CreateContainerFailed (f"{response.json}", error_code=response.status_code)
    
   


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









def create_flow(ovs_id,src_ip,dst_ip,dst_port,container_ip,container_port):
        
    


    #ricordare di fare 2 flow (andata e ritorno) e l'elenco dei flow creati
    #cancellazione basata su lastseen di onos che fa partire pure la cancellazione dei container

    flow1=f"""{
    "priority": 40000,
    "timeout": 0,
    "isPermanent": true,
    "deviceId": ovs_id,
    "treatment": {
      "instructions": [
        {
          "type": "OUTPUT",
          "port": "NORMAL"
        },
        {
          "type":"L3MODIFICATION",
          "subtype":"IPV4_DST",
          "ip":container_ip
          },
              
        {
          "type":"L4MODIFICATION",
          "subtype":"TCP_SRC",
          "tcpPort":container_port
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
          "ip": src_ip
        },
        {
          "type": "IPV4_DST",
          "ip": dst_ip
        },
        {
          "type": "TCP_DST",
          "tcpPort": dst_port
        },
      ]
    }
    }"""

    flow2=f""""""
    print(flow1)

    #send request to onos
    


