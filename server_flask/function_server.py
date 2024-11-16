from flask import Flask, request, jsonify
import os
import re
import random
import string
import json
import requests

#Directory for vms
VM_PATH = './vm'

#OVS 
ovs_bridge = "br0"

#Server Address for network configuration (da fare nel file di config)
NET_SERVER="http://127.0.0.1:5001"

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
        
        #network configuration
        #config.vm.network :forwarded_port, guest: port_vm, host: port_host, id: port_id
        config.vm.network "public_network", bridge: "{tap}", ip: "{ip}"

    end
    """

    with open(os.path.join(vagrantfile_path, 'Vagrantfile'), 'w') as vagrant_file:
        vagrant_file.write(vagrantfile_content)
    return


#Update CPU
def update_cpu(cpu, vm_name):
  
    # Read the contents of the Vagrantfile
    vagrantfile_path = os.path.join(VM_PATH, vm_name, "Vagrantfile")
    with open(vagrantfile_path, "r") as file:
        vagrantfile_content = file.readlines()
  
    new_cpu_value = "vb.cpus = " + cpu
    # Modify the CPU line
    for i, line in enumerate(vagrantfile_content):
        if re.search(r'vb\.cpus\s*=\s*\d+', line):
            vagrantfile_content[i] = re.sub(r'vb\.cpus\s*=\s*\d+', new_cpu_value, line)
            break

    # Write the updated contents back to the Vagrantfile
    with open(vagrantfile_path, "w") as file:
        file.writelines(vagrantfile_content)

    print(f"CPU setting updated to {cpu} in Vagrantfile.")


#Update RAM
def update_ram(ram, vm_name):
    
    # Read the contents of the Vagrantfile
    vagrantfile_path = os.path.join(VM_PATH, vm_name, "Vagrantfile")
    with open(vagrantfile_path, "r") as file:
        vagrantfile_content = file.readlines()

    new_memory_value = "vb.memory = " + ram
    # Modify the memory line
    for i, line in enumerate(vagrantfile_content):
        if re.search(r'vb\.memory\s*=\s*\d+', line):
            vagrantfile_content[i] = re.sub(r'vb\.memory\s*=\s*\d+', new_memory_value, line)
            break

    # Write the updated contents back to the Vagrantfile
    with open(vagrantfile_path, "w") as file:
        file.writelines(vagrantfile_content)

    print(f"Memory setting updated to {ram} MB in Vagrantfile.")


#Update IP
def update_ip(ip, vm_name):
    
    # Read the contents of the Vagrantfile
    vagrantfile_path = os.path.join(VM_PATH, vm_name, "Vagrantfile")
    with open(vagrantfile_path, "r") as file:
        vagrantfile_content = file.readlines()

    new_ip_value = 'ip: "' + ip + '"'
    # Modify the IP address line
    for i, line in enumerate(vagrantfile_content):
        if re.search(r'ip:\s*"\d+\.\d+\.\d+\.\d+"', line):
            vagrantfile_content[i] = re.sub(r'ip:\s*"\d+\.\d+\.\d+\.\d+"', new_ip_value, line)
            break

    # Write the updated contents back to the Vagrantfile
    with open(vagrantfile_path, "w") as file:
        file.writelines(vagrantfile_content)

    print(f"IP address updated to {ip} in Vagrantfile.")


#Define vm's id
def generate_unique_id(length=5):
    
    try:
        with open(os.path.join(VM_PATH, 'VM_list.json'), 'r') as vm_list:
            vm_dictionary = json.load(vm_list)
    except FileNotFoundError:
        return jsonify ({'error': f"VM_list doesn't exists."}), 404

    while True:

        vm_id = ''.join(random.choices(string.ascii_letters + string.digits, k=length))

        if vm_id not in vm_dictionary:
            return vm_id



# ********[DICTIONARY LIST VM]********

#Init dictionary
def init_int():
    vm_dictionary = {}
    
    #Read from id_list already existing interfaces
    try:
        with open(os.path.join(VM_PATH, 'VM_list.json'), 'r') as id_list:
            vm_dictionary = json.load(id_list)
    except FileNotFoundError:
        id_list = open(os.path.join(VM_PATH, 'VM_list.json'), 'w')
        id_list.write(json.dumps({}, indent=4))
        id_list.close()
    except json.JSONDecodeError as err:
        print (err)
    
    #Request creating already existing interfaces
    for key, value in vm_dictionary.items():
        veth_name = value.get("id")
        try:
            url= f"{NET_SERVER}/network/create_int/{veth_name}"
            response=requests.post(url,json="")
            print (response.json())
        except Exception as e:
            print (jsonify({"error": str(e)}), 400)

    return vm_dictionary


# Create item in vm dictionary
def create_item_vm_list(vm_name, id, ram, cpu, ip):

    try:
        with open(os.path.join(VM_PATH, 'VM_list.json'), 'r') as vm_list:
            vm_dictionary = json.load(vm_list)
    except FileNotFoundError as e:
        return jsonify ({'error': f"VM_list doesn't exists."}), 404

    vm_dictionary[vm_name] = {
        "id": id,
        "ram": ram,
        "cpu": cpu,
        "ip": ip,
        #"status": status
    }

    with open(os.path.join(VM_PATH, 'VM_list.json'), 'w') as vm_list:
        vm_list.write(json.dumps(vm_dictionary, indent=4))
    

# Update item in vm dictionary
def update_item_vm_list(vm_name, field, value_field):

    try:
        with open(os.path.join(VM_PATH, 'VM_list.json'), 'r') as vm_list:
            vm_dictionary = json.load(vm_list)
    except FileNotFoundError as e:
        return jsonify ({'error': f"VM_list doesn't exists."}), 404

    if vm_name in vm_dictionary:
        if field in vm_dictionary[vm_name]:
            vm_dictionary[vm_name][field] = value_field
        else:
           return jsonify({'error': f"Field '{field}' doesn't exists."}), 404
    else:
        return jsonify({'error': f"VM '{vm_name}' doesn't exists."}), 404
    
    with open(os.path.join(VM_PATH, 'VM_list.json'), 'w') as vm_list:
        vm_list.write(json.dumps(vm_dictionary, indent=4))

    return jsonify({'message': f"Field '{field}' successfully update to {value_field}."}), 200

#Search value of a field in dictionary
def search_item_vm_list(vm_name, field):

    try:
        with open(os.path.join(VM_PATH, 'VM_list.json'), 'r') as vm_list:
            vm_dictionary = json.load(vm_list)
    except FileNotFoundError as e:
        return jsonify ({'error': f"VM_list doesn't exists."}), 404

    if vm_name in vm_dictionary:
        if field in vm_dictionary[vm_name]:
            return vm_dictionary[vm_name][field]
        else:
           return jsonify({'error': f"Field '{field}' doesn't exists."}), 404
    else:
        return jsonify({'error': f"VM '{vm_name}' doesn't exists."}), 404

#Delete from dictionary
def delete_from_dictionary(vm_name):
    
    try:
        with open(os.path.join(VM_PATH, 'VM_list.json'), 'r') as vm_list:
            vm_dictionary = json.load(vm_list)
    except FileNotFoundError as e:
        return jsonify ({'error': f"VM_list doesn't exists."}), 404

    if vm_name in vm_dictionary:
        del vm_dictionary[vm_name]
    
        with open(os.path.join(VM_PATH, 'VM_list.json'), 'w') as vm_list:
            vm_list.write(json.dumps(vm_dictionary, indent=4))

