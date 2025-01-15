from time import sleep
from exceptions import *
from flask import Flask, jsonify, request, send_from_directory
import requests
import json


old_packet_count={}

def get_vm_list (VM_SERVER_URL):
 
  try:
      #Request to vm_configurator
      url= f"{VM_SERVER_URL}/vm/list"
      print (f"Sending request to '{url}' ...")
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
      print (f"Sending request to '{url}' ...")
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
      print (f"Sending request to '{url}' ...")
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
    print (f"Sending request to '{url}' ...")
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
    print (f"Sending request to '{url}' ...")
    payload={"service_port":f"{service_port}"}
    response=requests.post(url,json=payload,headers={"Content-Type": "application/json"})

    if (response.status_code == 201):
        print("Container created successfully!")
        print(response.json()["container"])
        return response.json()["container"]
    else:
        raise CreateContainerFailed (f"{response.json}", error_code=response.status_code)
    

def get_vm_ip_mac_by_name (vm_name, vmList):
    for vm in vmList:
        if vm["name"] == vm_name:
            return {"ip":vm["ip"],"mac":vm["mac"]} 

def choose_vm(vmList, containerCount, MAX_CONTAINERS):
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
    return chosen_vm


def create_flow_tcp(ONOS_URL, ONOS_AUTH_USERNAME, ONOS_AUTH_PASSWORD, ovs_id,attacker_ip,forbidden_ip,forbidden_port,container_ip,container_mac,container_vm_port):
        

    tcp_flow_attacker_honeypot={
    "flows": [
        {
            "priority": 50000,
            "timeout": 0,
            "isPermanent": "true",
            "deviceId": ovs_id,
            "treatment": {
                "instructions": [
                    {
                        "type": "L4MODIFICATION", 
                        "subtype":"TCP_DST", 
                        "tcpPort":container_vm_port 
                    },
                    {
                        "type": "L3MODIFICATION",
                        "subtype": "IPV4_DST",
                        "ip": container_ip
                    },
                    {
                        "type": "L2MODIFICATION",
                        "subtype": "ETH_DST",
                        "mac": container_mac
                    },
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
                        "type": "IP_PROTO",
                        "protocol": 6
                    },
                    {
                        "type": "IPV4_SRC",
                        "ip": attacker_ip+"/32"
                    },
                    {
                        "type": "IPV4_DST",
                        "ip": forbidden_ip+"/32"
                    },
                    {   
                        "type":"TCP_DST", 
                        "tcpPort":forbidden_port
                    }

                ]
            }
              }
          ]
      }

    #Request to onos flow
    url= f"{ONOS_URL}/onos/v1/flows"
    response=requests.post(url,json=tcp_flow_attacker_honeypot, auth=(ONOS_AUTH_USERNAME,ONOS_AUTH_PASSWORD))
    if (response.status_code == 200):
        print (response.json())
    else:
        raise CreateFlowFailed ("Error: Flow { attacker -> honeypot } not created.", error_code=response.status_code)


    tcp_flow_honeypot_attacker={
    "flows": [
        {
            "priority": 50000,
            "timeout": 0,
            "isPermanent": "true",
            "deviceId": ovs_id,
            "treatment": {
                "instructions": [
                  {
                        "type": "L4MODIFICATION", 
                        "subtype":"TCP_SRC", 
                        "tcpPort": forbidden_port
                    },
                    {
                        "type": "L3MODIFICATION",
                        "subtype": "IPV4_SRC",
                        "ip": forbidden_ip
                    },
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
                        "ip": container_ip+"/32"
                    },
                    {
                        "type": "IPV4_DST",
                        "ip": attacker_ip+"/32"
                    },
                    {   
                        "type":"TCP_SRC", 
                        "tcpPort": container_vm_port
                    }

                ]
            }
        }
        ]
    }
    
    #Request to onos flow
    url= f"{ONOS_URL}/onos/v1/flows"
    response=requests.post(url,json=tcp_flow_honeypot_attacker, auth=(ONOS_AUTH_USERNAME,ONOS_AUTH_PASSWORD))
    if (response.status_code == 200):
        print (response.json())
    else:
        raise CreateFlowFailed ("Error: Flow { honeypot -> attacker } not created.", error_code=response.status_code)



def flow_cleanup(ONOS_URL, ONOS_AUTH_USERNAME, ONOS_AUTH_PASSWORD, CONTAINER_SERVER_PORT):

    global old_packet_count
   
    try:
        print("-----------------------------------")
        #Request to onos flow
        url= f"{ONOS_URL}/onos/v1/flows"
        response=requests.get(url, auth=(ONOS_AUTH_USERNAME,ONOS_AUTH_PASSWORD))
        if (response.status_code == 200):
            new_flows = response.json()
        else:
            print("Flow list not obtained.", error_code=response.status_code)
        #Create dictionary
        new_packet_count={}
        for flow in new_flows["flows"]:
            if (flow["appId"] == "org.onosproject.rest" and  flow["priority"] >1 and flow.get("treatment", {}).get("instructions", [{}])[0].get("subtype")):
                
                #andata
                if(flow["treatment"]["instructions"][0]["subtype"]=="TCP_DST"):
                    port=flow["treatment"]["instructions"][0]["tcpPort"]
                    ip=flow["treatment"]["instructions"][1]["ip"]
                elif(flow["treatment"]["instructions"][0]["subtype"]=="UDP_DST"):
                    port=flow["treatment"]["instructions"][0]["udpPort"]
                    ip=flow["treatment"]["instructions"][1]["ip"]

                #ritorno
                elif(flow["treatment"]["instructions"][0]["subtype"]=="TCP_SRC"):
                    port=flow["selector"]["criteria"][4]["tcpPort"]
                    ip=flow["selector"]["criteria"][2]["ip"].split('/')[0]
                elif(flow["treatment"]["instructions"][0]["subtype"]=="UDP_SRC"):
                    port=flow["selector"]["criteria"][4]["udpPort"]
                    ip=flow["selector"]["criteria"][2]["ip"].split('/')[0]
    

                print(flow["treatment"]["instructions"][0]["subtype"])
                print("ip ",ip,"port " ,port)
                new_packet_count[flow["id"]]={"packets":flow["packets"], "ip": ip, "port":port, "device_id": flow["deviceId"]}

        #Verify packet number
        for id in new_packet_count:
            if(old_packet_count.get(id) !=None):
            
                if(new_packet_count[id]["packets"]>old_packet_count[id]["packets"]):
                    print("packets increased")
                elif(new_packet_count[id]["packets"]==old_packet_count[id]["packets"]):
                    print("packet number equal -> deleting flow ")
                    
                    try:
                        delete_container(new_packet_count[id]["ip"], CONTAINER_SERVER_PORT, new_packet_count[id]["port"])
                    except ContainerDeleteError as e:
                            print(f"Container not deleted {e}.")
                            
                    delete_flow(ONOS_URL, ONOS_AUTH_USERNAME, ONOS_AUTH_PASSWORD, new_packet_count[id]["device_id"], id)

            else:
                print("new flow")
        
        old_packet_count=new_packet_count

    


    except Exception as e:
        print(f"Error {e}.")


    
def delete_container(vm_ip, CONTAINER_SERVER_PORT, vm_port):
    
    try:
      #Request to container_configurator
      url= f"http://{vm_ip}:{CONTAINER_SERVER_PORT}/container/delete/byport/{vm_port}"
      print (f"Sending request to '{url}' ...")
      response=requests.delete(url)
      if (response.status_code == 200):
        response = response.json()
        print ("Response: ", response)
        return response
      else:
        raise ContainerDeleteError ("Error deleting container.", error_code=response.status_code)
    except requests.exceptions.ConnectionError:
        raise ServerNotRunning ("Container Server not running.", error_code=503)

def delete_flow(ONOS_URL, ONOS_AUTH_USERNAME, ONOS_AUTH_PASSWORD, device_id, flow_id):
    
    try:
        #Request to onos flow
        url= f"{ONOS_URL}/onos/v1/flows/{device_id}/{flow_id}"
        print (f"Sending request to '{url}' ...")
        response=requests.delete(url, auth=(ONOS_AUTH_USERNAME,ONOS_AUTH_PASSWORD))
        print ("Response: ", response)

        if (response.status_code != 204):
            raise OnosDeleteFlowError (f"Error deleting flow {flow_id}.", error_code=response.status_code)
    except requests.exceptions.ConnectionError as e:
        print(f"error. {e}")

