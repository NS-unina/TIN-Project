from flask import Flask, request, jsonify
from flask_cors import CORS
import vagrant
import os
import shutil

app = Flask (__name__)
app.config.from_object(__name__)

CORS(app,resources={r'/*':{'origins':'*'}})

#Directory dove creare le vm
VM_PATH = './vm'

#Creazione vagrantfile
def create_vagrantfile(name,box,cpus,ram,ip,tap):
    vm_path = os.path.join(VM_PATH,name)
    
    if os.path.exists(vm_path):
        raise FileExistsError()
    os.makedirs(vm_path)

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

    with open(os.path.join(vm_path, 'Vagrantfile'), 'w') as vagrant_file:
        vagrant_file.write(vagrantfile_content)
    return vm_path






@app.route('/create', methods=['POST'])
def create_vm():
    data = request.json
    vm_name = data.get('name')
    vm_box = data.get('box','generic/ubuntu2004')
    vm_cpus = data.get('cpus', '2') #default 2 CPU
    vm_ram = data.get ('ram', 1024) #default 1024 MB
    vm_ip=data.get('ip')
    vm_tap=data.get('int')


    if not vm_name:
        return jsonify({"error": "name field is needed"}), 400
    
    if not vm_ip:
        return jsonify({"error": "ip field is needed"}), 400
    
    if not vm_tap:
        return jsonify({"error": "tap field is needed"}), 400
    


    # Controlla che non esiste già la vm
    try:
        vm_path = create_vagrantfile(vm_name,vm_box, vm_cpus, vm_ram,vm_ip,vm_tap)
    except FileExistsError as e:
        return jsonify({"error": f"VM '{vm_name}' already exist. To modify it use the update request."}), 400 

    # Esegui vagrant up per avviare la VM
    try:
        v = vagrant.Vagrant(vm_path)
        v.up()
        return jsonify({"message": f"VM '{vm_name}' successfully created!"}), 201
    except Exception:
        return jsonify({"error": "Error creating vm"}), 500


@app.route('/delete/<vm_name>', methods=['DELETE'])
def delete_vm(vm_name):
    vm_path = os.path.join(VM_PATH, vm_name)

    if not os.path.exists(vm_path):
        return jsonify({"error": f"VM '{vm_name}' doesn't exist"}), 404

    try:
        v = vagrant.Vagrant(vm_path)
        v.destroy()
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


if __name__ == '__main__':
    os.makedirs(VM_PATH, exist_ok=True)
    app.run(host='0.0.0.0', port=5000)





