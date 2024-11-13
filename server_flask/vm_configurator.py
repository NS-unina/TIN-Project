from function_server import *
from flask_cors import CORS
import vagrant
import requests
import shutil


app = Flask (__name__)
app.config.from_object(__name__)

CORS(app,resources={r'/*':{'origins':'*'}})

#Server Address for network configuration (da fare nel file di config)
NET_SERVER="http://127.0.0.1:5001"


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

    try:
        if (vm_cpus):
            update_cpu(vm_cpus, vm_name)

        if (vm_ram):
            update_ram(vm_ram, vm_name)  
        
        if (vm_ip):
            update_ip(vm_ip, vm_name)
    except FileNotFoundError:
        return jsonify({"error": f" Vagrantfile for'{vm_name}' doesn't exist"}), 404

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




