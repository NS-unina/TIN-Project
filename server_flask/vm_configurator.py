from flask import Flask, request, jsonify
from flask_cors import CORS
import vagrant
import os
import requests
import shutil
import re
import random
import string
import json

app = Flask (__name__)
app.config.from_object(__name__)

CORS(app,resources={r'/*':{'origins':'*'}})

#Directory for vms
VM_PATH = './vm'

#Server Address for network configuration (da fare nel file di config)
NET_SERVER="http://127.0.0.1:5001"

#Dictionary ID
vm_id_dictionary = {}
try:
    with open(os.path.join(VM_PATH, 'ID_LIST'), 'r') as id_list:
            vm_id_dictionary = json.load(id_list)
except FileNotFoundError:
    id_list = open(os.path.join(VM_PATH, 'ID_LIST'), 'w')
    id_list.write(json.dumps({}))
    id_list.close()
except json.JSONDecodeError as err:
    print (err)
print (vm_id_dictionary)

#Creazione vagrantfile
def create_vagrantfile(vagrantfile_path,name,box,cpus,ram,ip,tap):
    
    #Contenuto vagrantfile
    vagrantfile_content= f"""
    Vagrant.configure("2") do |config|
        config.vm.box = "{box}"

        config.vm.provider "virtualbox" do |vb|
            vb.memory = {ram}
            vb.cpus = {cpus}
        end
    
        config.vm.provision "shell", path: "../init_vm.sh"
        #config.vm.provision "docker"
        config.vm.provision "file", source: "../app.py", destination: "app.py"
        
        #network configuration
        #config.vm.network :forwarded_port, guest: port_vm, host: port_host, id: port_id
        config.vm.network "public_network", bridge: "{tap}", ip: "{ip}"

    end
    """

    with open(os.path.join(vagrantfile_path, 'Vagrantfile'), 'w') as vagrant_file:
        vagrant_file.write(vagrantfile_content)
    return


#Update CPU
def update_cpu(cpu, vagrantfile_path):
    
    # Read the contents of the Vagrantfile
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
def update_ram(ram, vagrantfile_path):
    
    # Read the contents of the Vagrantfile
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
def update_ip(ip, vagrantfile_path):
    
    # Read the contents of the Vagrantfile
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
def generate_unique_id(vm_name, length=5):
    global vm_id_dictionary
    
    while True:

        vm_id = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
        
        print("generate_unique_id", vm_id_dictionary)

        
            

        if vm_id not in vm_id_dictionary:
            vm_id_dictionary[vm_name] = vm_id
        
            with open(os.path.join(VM_PATH, 'ID_LIST'), 'w') as id_list:
                id_list.write(json.dumps(vm_id_dictionary))
        
        return vm_id


#Delete from dictionary - vm_id
def delete_from_dictionary(vm_name):
    global vm_id_dictionary

    with open(os.path.join(VM_PATH, 'ID_LIST'), 'r') as id_list:
        vm_id_dictionary = json.load(id_list)


    if vm_name in vm_id_dictionary:
        del vm_id_dictionary[vm_name]
    
        with open(os.path.join(VM_PATH, 'ID_LIST'), 'w') as id_list:
                id_list.write(json.dumps(vm_id_dictionary))


@app.route('/create', methods=['POST'])
def create_vm():
    data = request.json
    vm_name = data.get('name')
    vm_box = data.get('box','generic/ubuntu2004')
    vm_cpus = data.get('cpus', '2') #default 2 CPU
    vm_ram = data.get ('ram', 1024) #default 1024 MB
    vm_ip=data.get('ip')


    if not vm_name:
        return jsonify({"error": "name field is needed"}), 400
    
    if not vm_ip:
        return jsonify({"error": "ip field is needed"}), 400
    
    #Check if vm already exist
    vm_path = os.path.join(VM_PATH, vm_name)
    if os.path.exists(vm_path):
        raise FileExistsError()
    os.makedirs(vm_path)

    #Generate vm_id
    vm_id = generate_unique_id(vm_name)
    print (vm_id_dictionary)

    #Create network interfaces for the VM
    try:
        url= f"{NET_SERVER}/network/create_int/{vm_id}"
        response=requests.post(url,json="")

        if (response.status_code == 200):
            print("Interface created successfully!")
            print(response.json())
            vm_interface = response.json()["interface"]
        else:
            return(f"Request failed with status code: {response.status_code}")

    except Exception as e:
        return jsonify({"error": str(e)}), 400

    print ("create:", vm_id_dictionary)
    #Creating vagrantfile
    try:
        create_vagrantfile(vm_path, vm_name,vm_box, vm_cpus, vm_ram, vm_ip, vm_interface)
    except FileExistsError as e:
        return jsonify({"error": f"VM '{vm_name}' already exist. To modify it use the update request."}), 400 

    #Starting the vm
    try:
        v = vagrant.Vagrant(vm_path)
        #v.up()
        return jsonify({"message": f"VM '{vm_name}' successfully created!"}), 201
    except Exception:
        return jsonify({"error": "Error deleting vm"}), 500


@app.route('/delete/<vm_name>', methods=['DELETE'])
def delete_vm(vm_name):
    global vm_id_dictionary

    #Check if vm exists
    vm_path = os.path.join(VM_PATH, vm_name)
    if not os.path.exists(vm_path):
        return jsonify({"error": f"VM '{vm_name}' doesn't exist"}), 404

    vm_id = vm_id_dictionary.get(vm_name)
    print (vm_id)

    try:
        url= f"{NET_SERVER}/network/delete_int/{vm_id}"
        response=requests.delete(url)

        if (response.status_code == 200):
            print("Interface deleted successfully!")
            delete_from_dictionary(vm_name)
            print ("delete:", vm_id_dictionary)
        else:
            return(f"Request failed with status code: {response.status_code}")

    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
    

    #Deleting vm and directory
    try:
        v = vagrant.Vagrant(vm_path)
        #v.destroy()
        shutil.rmtree(vm_path)
        return jsonify({"message": f"VM '{vm_name}' sucessfully deleted!"}), 200
    except Exception:
        return jsonify({"error": "Error deleting vm"}), 500


@app.route('/read', methods=['GET'])
def show_vm():
    
    vm_statuses = []
    try:
        for vm_name in os.listdir(VM_PATH):
            vm_path = os.path.join(VM_PATH, vm_name)
            if os.path.isdir(vm_path):
                v = vagrant.Vagrant(vm_path)
                status = v.status()

                for entry in status:
                    vm_statuses.append({
                        "name": vm_name,
                        "status": entry.state
                    })
    
        
        response={"vms": vm_statuses}
        return jsonify(response), 200

    except Exception:
        return jsonify({"error": "Error in reading vms status"}), 500


@app.route('/update/<vm_name>', methods=['POST'])
def update_vm(vm_name):
    data = request.json
    vm_cpus = data.get('cpus') 
    vm_ram = data.get ('ram') 
    vm_ip=data.get('ip')
    

    if ((not vm_cpus) and (not vm_ram) and (not vm_ip)):
        return jsonify({"error": "Field is needed"}), 400
    
    #Check if vm exist
    vm_path = os.path.join(VM_PATH, vm_name)
    if not os.path.exists(vm_path):
        return jsonify({"error": f"VM '{vm_name}' doesn't exist"}), 404

    vagrantfile_path = os.path.join(vm_path, "Vagrantfile")

    if (vm_cpus):
        update_cpu(vm_cpus, vagrantfile_path)

    if (vm_ram):
        update_ram(vm_ram, vagrantfile_path)  
    
    if (vm_ip):
        update_ip(vm_ip, vagrantfile_path)

    try:
        v = vagrant.Vagrant(vm_path)
        #v.reload()
        return jsonify({"message": f"VM '{vm_name}' sucessfully updated!.", "CPU": f"{vm_cpus}", "RAM": f"{vm_ram}", "IP": f"{vm_ip}"}), 200
    except Exception:
        return jsonify({"error": "Error updating vm"}), 500



@app.route('/start/<vm_name>', methods=['POST'])
def power_start_vm(vm_name):

#Check if vm exist
    vm_path = os.path.join(VM_PATH, vm_name)
    if not os.path.exists(vm_path):
        return jsonify({"error": f"VM '{vm_name}' doesn't exist"}), 404

    try:
        v = vagrant.Vagrant(vm_path)
        v.up()
        return jsonify({"message": f"VM '{vm_name}' successfully started!"}), 201
    except Exception:
        return jsonify({"error": "Error starting  vm"}), 500


@app.route('/stop/<vm_name>', methods=['POST'])
def power_stop_vm(vm_name):

#Check if vm exist
    vm_path = os.path.join(VM_PATH, vm_name)
    if not os.path.exists(vm_path):
        return jsonify({"error": f"VM '{vm_name}' doesn't exist"}), 404

    try:
        v = vagrant.Vagrant(vm_path)
        v.halt()
        return jsonify({"message": f"VM '{vm_name}' successfully stopped!"}), 201
    except Exception:
        return jsonify({"error": "Error stopping  vm"}), 500



@app.route('/reload/<vm_name>', methods=['POST'])
def power_vm(vm_name):

#Check if vm exist
    vm_path = os.path.join(VM_PATH, vm_name)
    if not os.path.exists(vm_path):
        return jsonify({"error": f"VM '{vm_name}' doesn't exist"}), 404

    try:
        v = vagrant.Vagrant(vm_path)
        v.reload()
        return jsonify({"message": f"VM '{vm_name}' successfully reloaded!"}), 201
    except Exception:
        return jsonify({"error": "Error reloading  vm"}), 500




if __name__ == '__main__':
    os.makedirs(VM_PATH, exist_ok=True)
    app.run(host='0.0.0.0', port=5000)




