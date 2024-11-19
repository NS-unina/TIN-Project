from time import sleep
from function_server import *
from flask import jsonify
from exception import *
from flask_cors import CORS
import vagrant
import shutil


from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime


app = Flask (__name__)
app.config.from_object(__name__)

CORS(app,resources={r'/*':{'origins':'*'}})


#check that network configurator server is running
while (True):

    try:
        url= f"{NET_SERVER}/network/ping"
        response=requests.get(url)
        if (response.status_code == 200):
            print("Network Configurator Running, initializing network interfaces\n")

            #Request init list of vm and creations of interfaces
            vm_id_dictionary = init_int()
            print (vm_id_dictionary)
            break     
    except requests.exceptions.ConnectionError as e:
        print("Network Configurator Server not found. Check if it's running and if the configured IP and Ports are correct\n")
    except Exception as e:
        print (jsonify({"error": f"Error {e}"}), 400)
    sleep(5)
    


# Periodic function to update vm
def sync_vm():

    try:
        for vm_name in os.listdir(VM_PATH):
            vm_path = os.path.join(VM_PATH, vm_name)
            if os.path.isdir(vm_path):
                v = vagrant.Vagrant(vm_path)
                status = v.status()
                update_item_vm_list(vm_name, "status", status[0].state)
                print ("ok")
    except VM_listFileNotFound as e:
        return ({"error": f"{e.message}"})
    except FieldNotValid as e:
        return ({'error': f"{e.message}"})
    except Exception as e:
        return ({"error": f"Error {e}"}), 500



# Configuration of BackgroundScheduler
scheduler = BackgroundScheduler()
scheduler.start()
scheduler.add_job(sync_vm, trigger=IntervalTrigger(seconds=15))




@app.route('/create', methods=['POST'])
def create_vm():
    data = request.json
    vm_name = data.get('name')
    vm_box = data.get('box','generic/ubuntu2004')
    vm_cpus = data.get('cpus', 2) #default 2 CPU
    vm_ram = data.get ('ram', 1024) #default 1024 MB
    vm_ip=data.get('ip')

    #Field needed
    if not vm_name:
        return jsonify({"error": "name field is needed"}), 400
    if not vm_ip:
        return jsonify({"error": "ip field is needed"}), 400
      
    try:
        #Create vm directory
        vm_path = os.path.join(VM_PATH, vm_name)
        os.makedirs(vm_path)

        #Generate vm_id
        vm_id = generate_unique_id()

        #Create network interfaces for the VM
        url= f"{NET_SERVER}/network/create_int/{vm_id}"
        response=requests.post(url,json="")
        if (response.status_code == 201):
            print("Interface created successfully!")
            print(response.json())
            vm_interface = response.json()["interface"]
        else:
            return jsonify({'error': f"Request failed with status code: {response.status_code}"})
        
        #Creating vagrantfile and save information in vm dictionary
        create_vagrantfile(vm_path, vm_name,vm_box, vm_cpus, vm_ram, vm_ip, vm_interface)
        create_item_vm_list(vm_name, vm_id, vm_ram, vm_cpus, vm_ip)

        #Starting the vm
        v = vagrant.Vagrant(vm_path)
        #v.up()
        status = v.status()
        update_item_vm_list(vm_name, "status", status[0].state)        
        return jsonify({"message": f"VM '{vm_name}' successfully created!"}), 201

    except FileExistsError:
        return jsonify({"error": f"VM '{vm_name}' already exist"}), 404
    except VM_listFileNotFound as e:
        return jsonify ({'error': f"VM_list doesn't exists."}), e.error_code
    except Exception as e:
        return jsonify({"error": f"Error creating vm. {e}"})



@app.route('/delete/<vm_name>', methods=['DELETE'])
def delete_vm(vm_name):

    try:
        #Check if vm already exist
        vm_path = os.path.join(VM_PATH, vm_name)
        if not os.path.exists(vm_path):
            return jsonify({"error": f"VM '{vm_name}' doesn't exist"}), 404

        #Find associated interface
        vm_id = search_item_vm_list(vm_name, "id")

        #Delete network interfaces for the VM
        url= f"{NET_SERVER}/network/delete_int/{vm_id}"
        response=requests.delete(url)
        if (response.status_code == 200):
            print("Interface deleted successfully!")
            delete_from_dictionary(vm_name)
        else:
            return jsonify({"error": f"Request failed with status code: {response.status_code}"})

        #Deleting vm and directory
        v = vagrant.Vagrant(vm_path)
        #v.destroy()
        shutil.rmtree(vm_path)
        return jsonify({"message": f"VM '{vm_name}' sucessfully deleted!"}), 200
    
    except VM_listFileNotFound as e:
        return jsonify ({'error': f"VM_list doesn't exists."}), e.error_code
    except FieldNotValid as e:
        return jsonify ({'error': f"{e.message}"}), e.error_code
    except Exception as e:
        return jsonify({"error": f"Error deleting vm. {e}"}), 500


@app.route('/read', methods=['GET'])
def read_vms():

    try:
        with open(os.path.join(VM_PATH, 'VM_list.json'), 'r') as vm_list:
            vm_dictionary = json.load(vm_list)
    
        vm_statuses = [{"name": key, **value} for key, value in vm_dictionary.items()]
        response={"vms": vm_statuses}
        return jsonify(response), 200
    
    except VM_listFileNotFound as e:
        return jsonify ({'error': f"VM_list doesn't exists."}), e.error_code
    except Exception as e:
        return jsonify({"error": f"Error in reading vms status. {e}"}), 500


@app.route('/update/<vm_name>', methods=['POST'])
def update_vm(vm_name):
    data = request.json
    vm_cpus = data.get('cpus') 
    vm_ram = data.get ('ram') 
    vm_ip=data.get('ip')

    if ((not vm_cpus) and (not vm_ram) and (not vm_ip)):
        return jsonify({"error": "At least one field of 'cpus', 'ram' or 'ip' is needed"}), 400
    
    try:
        #Check if vm already exist
        vm_path = os.path.join(VM_PATH, vm_name)
        if not os.path.exists(vm_path):
            return jsonify({"error": f"VM '{vm_name}' doesn't exist"}), 404

        if (vm_cpus):
            update_cpu(vm_cpus, vm_name)
            update_item_vm_list(vm_name, "cpu", vm_cpus)
        if (vm_ram):
            update_ram(vm_ram, vm_name)  
            update_item_vm_list(vm_name, "ram", vm_ram)
        if (vm_ip):
            update_ip(vm_ip, vm_name)
            update_item_vm_list(vm_name, "ip", vm_ip)

        v = vagrant.Vagrant(vm_path)
        #v.reload()
        status = v.status()
        update_item_vm_list(vm_name, "status", status[0].state)
        return jsonify({"message": f"VM '{vm_name}' sucessfully updated!.", "CPU": f"{vm_cpus}", "RAM": f"{vm_ram}", "IP": f"{vm_ip}"}), 200

    except VagrantfileNotFound as e:
        return jsonify({"error": f"{e.message}"}), 404
    except VM_listFileNotFound as e:
        return jsonify({"error": f"{e.message}"}), e.error_code
    except FieldNotValid as e:
        return jsonify ({'error': f"{e.message}"}), e.error_code
    except Exception as e:
        return jsonify({"error": f"Error updating vm. {e}"}), 500


@app.route('/start/<vm_name>', methods=['POST'])
def power_start_vm(vm_name):

    try:
        #Check if vm exist
        vm_path = os.path.join(VM_PATH, vm_name)
        if not os.path.exists(vm_path):
            return jsonify({"error": f"VM '{vm_name}' doesn't exist"}), 404

        #Starting the vm
        v = vagrant.Vagrant(vm_path)
        v.up()
        status = v.status()
        update_item_vm_list(vm_name, "status", status[0].state)
        return jsonify({"message": f"VM '{vm_name}' successfully started!"}), 200
    
    except VM_listFileNotFound as e:
        return jsonify({"error": f"{e.message}"}), e.error_code
    except FieldNotValid as e:
        return jsonify ({'error': f"{e.message}"}), e.error_code
    except Exception as e:
        return jsonify({"error": f"Error starting  vm. {e}"}), 500


@app.route('/stop/<vm_name>', methods=['POST'])
def power_stop_vm(vm_name):

    try:
        #Check if vm exist
        vm_path = os.path.join(VM_PATH, vm_name)
        if not os.path.exists(vm_path):
            return jsonify({"error": f"VM '{vm_name}' doesn't exist"}), 404
        
        #Stopping the vm
        v = vagrant.Vagrant(vm_path)
        v.halt()
        status = v.status()
        update_item_vm_list(vm_name, "status", status[0].state)
        return jsonify({"message": f"VM '{vm_name}' successfully stopped!"}), 200
    
    except VM_listFileNotFound as e:
        return jsonify({"error": f"{e.message}"}), e.error_code
    except FieldNotValid as e:
        return jsonify ({'error': f"{e.message}"}), e.error_code
    except Exception as e:
        return jsonify({"error": f"Error starting  vm. {e}"}), 500



@app.route('/reload/<vm_name>', methods=['POST'])
def power_vm(vm_name):

    try:
        #Check if vm exist
        vm_path = os.path.join(VM_PATH, vm_name)
        if not os.path.exists(vm_path):
            return jsonify({"error": f"VM '{vm_name}' doesn't exist"}), 404

        #Reloading the vm
        v = vagrant.Vagrant(vm_path)
        v.reload()
        status = v.status()
        update_item_vm_list(vm_name, "status", status[0].state)
        return jsonify({"message": f"VM '{vm_name}' successfully reloaded!"}), 201
    
    except VM_listFileNotFound as e:
        return jsonify({"error": f"{e.message}"}), e.error_code
    except FieldNotValid as e:
        return jsonify ({'error': f"{e.message}"}), e.error_code
    except Exception as e:
        return jsonify({"error": f"Error starting  vm. {e}"}), 500




if __name__ == '__main__':
    os.makedirs(VM_PATH, exist_ok=True)
    app.run(host='0.0.0.0', port=5000)

    try:
        app.run(debug=True, use_reloader=False)  # use_reloader=False evita conflitti con APScheduler
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()  # Assicura che lo scheduler venga fermato correttamente


