from flask import Flask, request
from exception import *
import os
import re
import random
import string
import json
import requests
import vagrant


#Directory for vms
#VM_PATH = '../vm'

#Server Address for network configuration (da fare nel file di config)
#NET_SERVER="http://127.0.0.1:5001"

#Vagrantfile creation
def create_vagrantfile(vagrantfile_path,name,box,cpus,ram,ip,tap):
    
    vagrantfile_content= f"""
    Vagrant.configure("2") do |config|
        config.vm.box = "{box}"
        config.vm.hostname = "{name}"

        config.vm.provider "virtualbox" do |vb|
            vb.memory = {ram}
            vb.cpus = {cpus}
        end
    
        config.vm.provision "shell", path: "../init_vm.sh"
        config.vm.provision "docker"
        config.vm.provision "file", source: "../container_configurator.py", destination: "app.py"
        config.vm.provision "file", source: "../function_container.py", destination: "function_container.py"
        config.vm.provision "file", source: "../exception_container.py", destination: "exception_container.py"

        #network configuration
        config.vm.network :forwarded_port, guest: 5002, host: 5002, id: "container_server"
        config.vm.network "public_network", bridge: "{tap}", ip: "{ip}"

    end
    """

    with open(os.path.join(vagrantfile_path, 'Vagrantfile'), 'w') as vagrant_file:
        vagrant_file.write(vagrantfile_content)
    return

#Define vm's id
def generate_unique_id(VM_PATH,length=5):
    
    try:
        with open(os.path.join(VM_PATH, 'VM_list.json'), 'r') as vm_list:
            vm_dictionary = json.load(vm_list)
    except FileNotFoundError:
        raise VM_listFileNotFound ("VM_list doesn't exists.", error_code=404)

    while True:

        vm_id = ''.join(random.choices(string.ascii_letters + string.digits, k=length))

        if vm_id not in vm_dictionary:
            return vm_id


# ********[FUNCTION FOR VM STATUS]********

# Restore vm based on last status
def restore_vm_status (VM_PATH):
    try:
        with open(os.path.join(VM_PATH, 'VM_list.json'), 'r') as vm_list:
            vm_dictionary = json.load(vm_list)
    except FileNotFoundError as e:
        raise VM_listFileNotFound ("VM_list doesn't exists.", error_code=404)

    for vm_name in vm_dictionary:
        status = vm_dictionary[vm_name]["status"]

        #Check if vm folder exists
        vm_path = os.path.join(VM_PATH, vm_name)
        if not os.path.exists(vm_path):
            raise VmNotFound (f"VM '{vm_name}' not found.", error_code=404)
        
        #Check if vagrantfile exist
        vagrantfile_path = os.path.join(VM_PATH, vm_name, "Vagrantfile")
        if not os.path.exists(vagrantfile_path):
            raise VagrantfileNotFound ("Vagrantfile not found.", error_code=404)

        v = vagrant.Vagrant(vm_path)
        if status == "running":
            v.up()
            print (f"VM {vm_name} restored to running.")
        elif status == "poweroff":
            v.halt()
            print (f"VM {vm_name} restored to poweroff.")



# Periodic function to update vm
def sync_vm(VM_PATH):
    try:
        for vm_name in os.listdir(VM_PATH):
            vm_path = os.path.join(VM_PATH, vm_name)
            if os.path.isdir(vm_path):
                if (not os.path.exists(os.path.join(vm_path,"Vagrantfile"))):
                    continue                   
                v = vagrant.Vagrant(vm_path)
                status = v.status()
                update_item_vm_list(vm_name, "status", status[0].state,VM_PATH)
                print ("ok")

    except VagrantfileNotFound as e:
        print ({"error": f"{e.message}"})
    except VM_listFileNotFound as e:
        print ({"error": f"{e.message}"})
    except FieldNotValid as e:
        print ({'error': f"{e.message}"})
    except Exception as e:
        print ({"error": f"Error {e}"})



# ********[UPDATE FIELD IN VAGRANTFILE]********

#Update CPU
def update_cpu(cpu, vm_name,VM_PATH):
    
    try:
        # Read the contents of the Vagrantfile
        vagrantfile_path = os.path.join(VM_PATH, vm_name, "Vagrantfile")
        with open(vagrantfile_path, "r") as vagrantfile:
            vagrantfile_content = vagrantfile.readlines()
    except FileNotFoundError as e:
        raise VagrantfileNotFound ("Vagrantfile not found.", error_code=404)
  
    new_cpu_value = "vb.cpus = " + cpu
    # Modify the CPU line
    for i, line in enumerate(vagrantfile_content):
        if re.search(r'vb\.cpus\s*=\s*\d+', line):
            vagrantfile_content[i] = re.sub(r'vb\.cpus\s*=\s*\d+', new_cpu_value, line)
            break

    # Write the updated contents back to the Vagrantfile
    with open(vagrantfile_path, "w") as vagrantfile:
        vagrantfile.writelines(vagrantfile_content)


#Update RAM
def update_ram(ram, vm_name,VM_PATH):
    
    try:
        # Read the contents of the Vagrantfile
        vagrantfile_path = os.path.join(VM_PATH, vm_name, "Vagrantfile")
        with open(vagrantfile_path, "r") as vagrantfile:
            vagrantfile_content = vagrantfile.readlines()
    except FileNotFoundError as e:
        raise VagrantfileNotFound ("Vagrantfile not found.", error_code=404)

    new_memory_value = "vb.memory = " + ram
    # Modify the memory line
    for i, line in enumerate(vagrantfile_content):
        if re.search(r'vb\.memory\s*=\s*\d+', line):
            vagrantfile_content[i] = re.sub(r'vb\.memory\s*=\s*\d+', new_memory_value, line)
            break

    # Write the updated contents back to the Vagrantfile
    with open(vagrantfile_path, "w") as vagrantfile:
        vagrantfile.writelines(vagrantfile_content)


#Update IP
def update_ip(ip, vm_name,VM_PATH):
    
    try:
        # Read the contents of the Vagrantfile
        vagrantfile_path = os.path.join(VM_PATH, vm_name, "Vagrantfile")
        with open(vagrantfile_path, "r") as vagrantfile:
            vagrantfile_content = vagrantfile.readlines()
    except FileNotFoundError as e:
        raise VagrantfileNotFound ("Vagrantfile not found.", error_code=404)

    new_ip_value = 'ip: "' + ip + '"'
    # Modify the IP address line
    for i, line in enumerate(vagrantfile_content):
        if re.search(r'ip:\s*"\d+\.\d+\.\d+\.\d+"', line):
            vagrantfile_content[i] = re.sub(r'ip:\s*"\d+\.\d+\.\d+\.\d+"', new_ip_value, line)
            break

    # Write the updated contents back to the Vagrantfile
    with open(vagrantfile_path, "w") as vagrantfile:
        vagrantfile.writelines(vagrantfile_content)



# ********[DICTIONARY LIST VM]********

#Init dictionary
def init_int(NET_SERVER,VM_PATH):
    vm_dictionary = {}
    
    #Read from id_list already existing interfaces
    try:
        with open(os.path.join(VM_PATH, 'VM_list.json'), 'r') as vm_list:
            vm_dictionary = json.load(vm_list)
    except FileNotFoundError:
        vm_list = open(os.path.join(VM_PATH, 'VM_list.json'), 'w')
        vm_list.write(json.dumps({}, indent=4))
        vm_list.close()
    except json.JSONDecodeError as err:
        print (err)
    
    #Request creating already existing interfaces
    for key, value in vm_dictionary.items():
        veth_name = value.get("id")

        url= f"{NET_SERVER}/network/create_int/{veth_name}"
        response=requests.post(url,json="")
        print (response.json())

    return vm_dictionary


# Create item in vm dictionary
def create_item_vm_list(vm_name, id, ram, cpu, ip,VM_PATH):

    try:
        with open(os.path.join(VM_PATH, 'VM_list.json'), 'r') as vm_list:
            vm_dictionary = json.load(vm_list)
    except FileNotFoundError as e:
        raise VM_listFileNotFound ("VM_list doesn't exists.", error_code=404)

    vm_dictionary[vm_name] = {
        "id": id,
        "ram": ram,
        "cpu": cpu,
        "ip": ip,
        "status": "not created"
    }

    with open(os.path.join(VM_PATH, 'VM_list.json'), 'w') as vm_list:
        vm_list.write(json.dumps(vm_dictionary, indent=4))
    

# Update item in vm dictionary
def update_item_vm_list(vm_name, field, value_field,VM_PATH):

    try:
        with open(os.path.join(VM_PATH, 'VM_list.json'), 'r') as vm_list:
            vm_dictionary = json.load(vm_list)
    except FileNotFoundError:
        raise VM_listFileNotFound ("VM_list doesn't exists.", error_code=404)

    if vm_name in vm_dictionary:
        if field in vm_dictionary[vm_name]:
            vm_dictionary[vm_name][field] = value_field
        else:
           raise FieldNotValid (f"Field '{field}' doesn't exists.", error_code=400)
    else:
        raise FieldNotValid (f"VM '{vm_name}' doesn't exists.", error_code=400)
    
    with open(os.path.join(VM_PATH, 'VM_list.json'), 'w') as vm_list:
        vm_list.write(json.dumps(vm_dictionary, indent=4))


#Search value of a field in dictionary
def search_item_vm_list(vm_name, field,VM_PATH):

    try:
        with open(os.path.join(VM_PATH, 'VM_list.json'), 'r') as vm_list:
            vm_dictionary = json.load(vm_list)
    except FileNotFoundError as e:
        raise VM_listFileNotFound ("VM_list doesn't exists.", error_code=404)

    if vm_name in vm_dictionary:
        if field in vm_dictionary[vm_name]:
            return vm_dictionary[vm_name][field]
        else:
           raise FieldNotValid (f"Field '{field}' doesn't exists.", error_code=400)
    else:
        raise FieldNotValid (f"VM '{vm_name}' doesn't exists.", error_code=400)

#Delete from dictionary
def delete_from_dictionary(vm_name,VM_PATH):
    
    try:
        with open(os.path.join(VM_PATH, 'VM_list.json'), 'r') as vm_list:
            vm_dictionary = json.load(vm_list)
    except FileNotFoundError as e:
        raise VM_listFileNotFound ("VM_list doesn't exists.", error_code=404)

    if vm_name in vm_dictionary:
        del vm_dictionary[vm_name]
    
        with open(os.path.join(VM_PATH, 'VM_list.json'), 'w') as vm_list:
            vm_list.write(json.dumps(vm_dictionary, indent=4))


