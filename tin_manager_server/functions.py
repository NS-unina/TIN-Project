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
  

def get_container_by_service (CONTAINER_SERVER_URL, service_port):
 
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

    response=requests.post(url,json={}) 
    if (response.status_code == 201):
        print("Vm created successfully!")
        return response.json()["vm"]
    else:
      raise CreateVmFailed (f"{response.json}", error_code=response.status_code)
    
  except requests.exceptions.ConnectionError:
    raise ServerNotRunning ("VM Server not running. Can not configure vms list.", error_code=503)


def create_container(vm_ip,CONTAINER_SERVER_PORT,service_port): 

    url= f"http://{vm_ip}:{CONTAINER_SERVER_PORT}/container/create"
    
    payload={"service_port":f"{service_port}"}
    headers = {"Content-Type": "application/json"}
    
    response=requests.post(url,json=payload,headers=headers)

    if (response.status_code == 201):
        print("Container created successfully!")
        print(response.json()["container"])
        return response.json()["container"]
    else:
        raise CreateContainerFailed (f"{response.json}", error_code=response.status_code)
    

def get_vm_ip_by_name (vm_name, vmList):
    for vm in vmList:
        if vm["name"] == vm_name:
            return vm["ip"]



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
    


