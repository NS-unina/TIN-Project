from flask import Flask, request
from exceptions import *
import os
import re
import random
import string
import requests
import vagrant
import ipaddress

#Init interfaces
def init_int(NET_SERVER,collection):

    ids = collection.find({}, {"_id": 0, "id": 1})

    for item in ids:
        url= f"{NET_SERVER}/network/create_int/{item["id"]}"
        response=requests.post(url,json="")
        print (f"Inizialized interface {item["id"]}. Network server response: {response.json()}")
    return

#Vagrantfile creation
def create_vagrantfile(vagrantfile_path,name,box,cpus,ram,ip,mac,interface):
    
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
        config.vm.provision "file", source: "../../container_server/container_configurator.py", destination: "app.py"
        config.vm.provision "file", source: "../../container_server/functions.py", destination: "functions.py"
        config.vm.provision "file", source: "../../container_server/exceptions.py", destination: "exceptions.py"
        config.vm.provision "file", source: "../../container_server/config.py", destination: "config.py"

        #network configuration
        #config.vm.network :forwarded_port, guest: 5002, host: 5002, id: "container_server"
        config.vm.network "public_network", bridge: "{interface}", ip: "{ip}", mac: "{mac}"

    end
    """

    with open(os.path.join(vagrantfile_path, 'Vagrantfile'), 'w') as vagrant_file:
        vagrant_file.write(vagrantfile_content)
    return

# #Define vm's id
def generate_unique_id(collection,length=5):
 
    id_list = collection.find({}, {"_id": 0, "id": 1})
    while True:
        vm_id = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
        if vm_id not in id_list:
            print (vm_id)
            return vm_id
    

def generate_default_ip(collection, network, excluded_ips):

    result = collection.find({}, {"_id": 0, "ip": 1})
    ip_addresses = ipaddress.ip_network(network, strict=False)

    ips_not_available = [doc["ip"] for doc in result if "ip" in doc]
    
    for ip in ip_addresses.hosts():
        if str(ip) not in (ips_not_available + excluded_ips):
            return str(ip)
    
    #Ip not found
    raise DefaultIpNotAvailable ("Default IP not available.", error_code=400)

def generate_default_mac (collection):

    used_mac = collection.find({}, {"_id": 0, "mac": 1})
    while True:

        mac = "020000%02x%02x%02x" % (random.randint(0, 255),
                             random.randint(0, 255),
                             random.randint(0, 255))

        if mac not in used_mac:
            print (mac)
            return mac
        
    

# ********[FUNCTION FOR VM STATUS]********

# Restore vm based on last status
def restore_vm_status (VM_PATH,collection): 

    for vm in collection.find({}, {"_id": 0, "name": 1,"status": 1}):

        #Check if vm folder exists
        vm_path = os.path.join(VM_PATH, vm["name"])
        if not os.path.exists(vm_path):
            raise VmNotFound (f"VM '{vm["name"]}' not found.", error_code=404)
        
        #Check if vagrantfile exist
        vagrantfile_path = os.path.join(VM_PATH, vm["name"], "Vagrantfile")
        if not os.path.exists(vagrantfile_path):
            raise VagrantfileNotFound (f"Vagrantfile for {vm["name"]} not found.", error_code=404)

        v = vagrant.Vagrant(vm_path)
        if vm["status"] == "running":
            print (f"Restoring vm {vm["name"]} to running...")
            v.up()
        elif vm["status"] == "poweroff":
            print (f"Restoring vm {vm["name"]} to poweroff...")
            v.halt()
            

# Periodic function to update vm
def sync_vm(VM_PATH, collection):

    for vm_name in os.listdir(VM_PATH):
        try:
            vm_path = os.path.join(VM_PATH, vm_name)
            if os.path.isdir(vm_path):
                if (not os.path.exists(os.path.join(vm_path,"Vagrantfile"))):
                    continue                   
                v = vagrant.Vagrant(vm_path)
                status = v.status()
                update_item_vm_list(vm_name, "status", status[0].state, collection)
                print (f"Updated vm '{vm_name}' status")

        except VagrantfileNotFound as e:
            print ({"Error updating vms status": f"{e.message}"})
        except VmNotFound as e:
            print ({"Error updating vms status": f"{e.message}"})
        except ItemNotModified as e:
            print ("Nothing to update")
            pass
        except pymongo.errors.ConnectionFailure as e:
            print ({"Error updating vms status": "Connection to database failed."})
        except Exception as e:
            print ({"Error updating vms status": f"Error {e}"})



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
# Create item in vm dictionary
def create_item_vm_list(vm_name, id, ram, cpu, ip, mac, box, collection):

    newvm = {
        "name": vm_name,
        "id": id,
        "ram": ram,
        "cpu": cpu,
        "ip": ip,
        "mac": mac,
        "box": box,
        "status": "not created"
    }

    result = collection.insert_one(newvm)
    if (not result):
        raise FailedInsertion(f"Insert of vm {vm_name} failed", error_code=500)

    newvm.pop("_id", None)
    return newvm 
    



# Update image priority in service list
def update_priority_service_list(image, service_port, priority, collection):

    result = collection.update_one({"image": image},
                                   {"$set": {"services.$[service].priority": priority }},
                                    array_filters=[{"service.service_port": service_port}])

    if (result.matched_count==0):
        raise ImageNotFound (f"Can not find image '{image}'.", error_code=404)
    if(result.modified_count==0):
        raise ItemNotModified (f"Priority  in '{service_port}' not modified.", error_code=200)


# Update item in vm list
def update_item_vm_list(vm_name, field, value_field, collection):

    result = collection.update_one(
        {"name": vm_name},            
        {"$set": {field: value_field}}
        )
    
    if (result.matched_count==0):
        raise VmNotFound (f"Can not find vm '{vm_name}'.", error_code=404)
    if(result.modified_count==0):
        raise ItemNotModified (f"Field '{field}' in '{vm_name}' not modified.", error_code=200)
    

#Search value of a field in vm list
def search_item_vm_list(vm_name, field, collection):

    item = collection.find_one({"name": vm_name }, {"_id": 0 , f"{field}":1})
    if (not item):
        raise ItemNotFound (f"Field '{field}' in '{vm_name}' not found.", error_code=404)
    return item[field]


#Delete from 
def delete_from_list(vm_name, collection):

    result = collection.delete_one({"name": vm_name})
    if (result.deleted_count==0):
        raise ItemNotFound (f"Cannot delete vm {vm_name} ", error_code=400) 
 

def delete_containers_by_vm (vm_name, containerCollection):
    
    result = containerCollection.delete_many({"vm_name": vm_name})
    if (result.deleted_count==0):
        print("message: No containers to delete.")
    else:
        print (f"{result.deleted_count} containers deleted.")
        return


# ********[DATABASE FUNCTION]********
def check_database_exists (mongo, database_name):
    dblist = mongo.list_database_names()
    if not (f"{database_name}" in dblist):
        raise DatabaseNotFound (f"Database {database_name} not found.", error_code=404)

def check_collection_exists (mongo, database_name, collection_name):
    check_database_exists(mongo, database_name)
    collist = database_name.list_collection_names()
    if not (f"{collection_name}" in collist):
        raise CollectionNotFound (f"Collection {database_name} not found.", error_code=404)