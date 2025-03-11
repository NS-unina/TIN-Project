from functions import *
from exceptions import *
from validation_schemas import *
from config import DevelopmentConfig

from flask import jsonify, send_from_directory
from time import sleep
from shutil import rmtree
import vagrant
import pymongo

from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger



# ********[ LOAD CONFIGURATION FROM config.py ]********
app = Flask (__name__)
app.config.from_object(DevelopmentConfig)
CORS(app,resources={r'/*':{'origins':'*'}})

#Directory for vms
VM_PATH = app.config['VM_PATH']

#Server Address for network configuration 
NET_SERVER_URL=f"http://{app.config['NET_SERVER_IP']}:{app.config['NET_SERVER_PORT']}"

#Default network for vms and exluded addresses
DEFAULT_NETWORK = app.config['DEFAULT_NETWORK']
EXCLUDED_ADDRESSES = app.config['EXCLUDED_ADDRESSES']

#Database connection
DATABASE_CONNECTION = app.config['DATABASE_CONNECTION']



# ********[ STARTUP ]********
while True:
    try:
        print ("Attempting to connect to database and network server...")
        #Connection to database
        mongo = pymongo.MongoClient(DATABASE_CONNECTION)
        database = mongo["tinDatabase"] 
        vmCollection = database["vmList"]
        containerCollection = database["containerList"]
        serviceCollection = database["serviceList"]
        vmCollection.create_index("name", unique=True)

        # Attempt to connect to the network server
        url = f"{NET_SERVER_URL}/network/ping"
        response = requests.get(url)
        
        # Initialize interfaces
        print ("\nInitializing interfaces ... ")
        if response.status_code == 200:
            init_int(NET_SERVER_URL, vmCollection)
        else:
            raise NetworkServerError (f"Failed initializing interfaces. Response: {response.json}", error_code=response.status_code)
        
        # Restore vm's last state
        print ("\nRestoring vm's last state ... ")
        #restore_vm_status(VM_PATH, vmCollection)

        print ("\nSTARTUP DONE")
        break

    except requests.exceptions.ConnectionError as e:
        print("[ERROR] Connection to network configurator failed. Retrying...")
        sleep(7)
    except pymongo.errors.ConnectionFailure as e:
        print ("[ERROR] Connection to database failed. Trying to reconnect...")
        sleep(1)
    except NetworkServerError as e:
        print (e.message)
    except (VmNotFound, VagrantfileNotFound) as e:
        print (f"Could not restore vms status. {e.message}")
        break
    except Exception as e:
        print(jsonify({"error": f"{str(e)}"}))
        break


# Configuration of BackgroundScheduler
scheduler = BackgroundScheduler()
scheduler.start()
scheduler.add_job(lambda: sync_vm(VM_PATH, vmCollection), trigger=IntervalTrigger(seconds=15))


# ********[ API ]********
@app.route('/vm/create', methods=['POST'])
def create_vm():

    data = request.json
    try:
        validated_data = VMSchema().load(data)
    except ValidationError as e:
        return jsonify({"error": f"{e}"}), 400

    #Generate vm_id
    vm_id = generate_unique_id(vmCollection)

    vm_name = data.get('name') or  f'{vm_id}'
    vm_box = data.get('box') or 'generic/ubuntu2004'
    vm_cpus = data.get('cpus') or 2 #default 2 CPU
    vm_ram = data.get ('ram') or 1024 #default 1024 MB  
      
    try:
        #Check if vm exist
        check_vm = vmCollection.find_one({"name": vm_name}, {"_id": 0})
        if check_vm:
            return jsonify({"error": f"VM '{vm_name}' already exist"}), 400
        
        #Generate IP and MAC
        default_ip = generate_default_ip(vmCollection, DEFAULT_NETWORK, EXCLUDED_ADDRESSES)
        vm_ip=data.get('ip') or f'{default_ip}'
        vm_mac = generate_default_mac (vmCollection)

        #Create vm directory
        vm_path = os.path.join(VM_PATH, vm_name)
        os.makedirs(vm_path)
        
        #Create network interfaces for the VM
        url= f"{NET_SERVER_URL}/network/create_int/{vm_id}"
        response=requests.post(url,json="")
        if (response.status_code == 201):
            print(f"Interface created successfully!. Response: {response.json()}")
            vm_interface = response.json()["interface"]
        else:
            return jsonify({'error': f"Request failed."}), response.status_code

        #Creating vagrantfile and save information in vm dictionary
        create_vagrantfile(vm_path, vm_name,vm_box, vm_cpus, vm_ram, vm_ip, vm_mac, vm_interface)
        vm = create_item_vm_list(vm_name, vm_id, vm_ram, vm_cpus, vm_ip, vm_mac, vm_box, vmCollection)

        #Starting the vm
        v = vagrant.Vagrant(vm_path)
        #v.up()
        status = v.status()
        update_item_vm_list(vm_name, "status", status[0].state, vmCollection)        
        return jsonify({"message": f"VM '{vm_name}' successfully created!", "vm": vm}), 201

    except DefaultIpNotAvailable as e:
        return jsonify({"error": "Could not obtain default ip. Ip field is needed"}), 400
    except FileExistsError:
        return jsonify({"error": f"VM '{vm_name}' already exist"}), 409
    except requests.exceptions.ConnectionError as e:
        return jsonify({'error': 'Network configurator Server not running.'}), 500
    except pymongo.errors.ConnectionFailure as e:
        return jsonify({'error': 'Connection to database failed.'}), 500
    except FailedInsertion as e:
        return jsonify({'error': f'{e.message}'}), 500
    except Exception as e:
        return jsonify({"error": f"Error creating vm. {e}"}), 500



@app.route('/vm/delete/<vm_name>', methods=['DELETE'])
def delete_vm(vm_name):

    try:
        validated_data = VMNameSchema().load({"vm_name":vm_name})
    except ValidationError as e:
        return jsonify({"error": f"{e}"}), 400

    try:
        #Check if vm exist
        vm = vmCollection.find_one({"name": vm_name }, {"_id": 0})
        if (not vm):
            return jsonify({"error": f"VM '{vm_name}' doesn't exist"}), 404
        
        vm_path = os.path.join(VM_PATH, vm_name)
        if not os.path.exists(vm_path):
            return jsonify({"error": f"VM '{vm_name}' folder doesn't exist"}), 404

        #Find associated interface
        vm_id = search_item_vm_list(vm_name, "id", vmCollection)

        #Delete network interfaces for the VM
        url= f"{NET_SERVER_URL}/network/delete_int/{vm_id}"
        response=requests.delete(url)
        if (response.status_code != 200):
            return jsonify({"error": f"Request failed. Response: {response.json()}"}), response.status_code
        print(f"Interface deleted successfully!. Response: {response.json()}")
        
        #Deleting vm and directory
        v = vagrant.Vagrant(vm_path)
        v.destroy()
        delete_containers_by_vm (vm_name, containerCollection)
        delete_from_list(vm_name,vmCollection)
        rmtree(vm_path)
        return jsonify({"message": f"VM '{vm_name}' sucessfully deleted!"}), 200
    
    except ItemNotFound as e:
        return jsonify ({'error': f"{e.message}"}), 404
    except requests.exceptions.ConnectionError as e:
        return jsonify({'error': 'Network configurator Server not running.'}), 500
    except pymongo.errors.ConnectionFailure as e:
        return jsonify({'error': 'Connection to database failed.'}), 500
    except Exception as e:
        return jsonify({"error": f"Error deleting vm. {e}"}), 500


@app.route('/vm/list', methods=['GET'])
def list_vms():

    try:
        vmlist = list(vmCollection.find({} ,{"_id": 0}))
        return jsonify(vmlist), 200
    except pymongo.errors.ConnectionFailure as e:
        return jsonify({'error': 'Connection to database failed.'}), 500
    except Exception as e:
        return jsonify({"error": f"Error in reading vms status. {e}"}), 500


@app.route('/vm/update/<vm_name>', methods=['POST'])
def update_vm(vm_name):

    data = request.json
    try:
        validated_data = VMNameSchema().load({"vm_name":vm_name})
        validated_data = VMUpdateSchema().load(data)
    except ValidationError as e:
        return jsonify({"error": f"{e}"}), 400

    vm_cpus = data.get('cpus') 
    vm_ram = data.get ('ram') 
    vm_ip = data.get('ip')

    if ((not vm_cpus) and (not vm_ram) and (not vm_ip)):
        return jsonify({"error": "At least one field of 'cpus', 'ram' or 'ip' is needed"}), 400
    
    try:
        #Check if vm exist
        vm = vmCollection.find_one({"name": vm_name }, {"_id": 0})
        if (not vm):
            return jsonify({"error": f"VM '{vm_name}' doesn't exist"}), 404
        
        vm_path = os.path.join(VM_PATH, vm_name)
        if not os.path.exists(vm_path):
            return jsonify({"error": f"VM '{vm_name}' folder doesn't exist"}), 404

        #Update operations
        if (vm_cpus):
            update_cpu(vm_cpus, vm_name,VM_PATH)
            update_item_vm_list(vm_name, "cpu", vm_cpus, vmCollection)
        if (vm_ram):
            update_ram(vm_ram, vm_name,VM_PATH)  
            update_item_vm_list(vm_name, "ram", vm_ram, vmCollection)
        if (vm_ip):
            update_ip(vm_ip, vm_name,VM_PATH)
            update_item_vm_list(vm_name, "ip", vm_ip, vmCollection)

        v = vagrant.Vagrant(vm_path)
        #v.reload()
        return jsonify({"message": f"VM '{vm_name}' sucessfully updated!.", "CPU": f"{vm_cpus}", "RAM": f"{vm_ram}", "IP": f"{vm_ip}"}), 200

    except VagrantfileNotFound as e:
        return jsonify({"error": f"{e.message}"}), 404
    except VmNotFound as e:
        return jsonify({"error": f"{e.message}"}), 404
    except ItemNotModified as e:
        return jsonify ({'message': f"{e.message}"}), 200
    except pymongo.errors.ConnectionFailure as e:
        return jsonify({'error': 'Connection to database failed.'}), 500
    except Exception as e:
        return jsonify({"error": f"Error updating vm. {e}"}), 500


@app.route('/vm/start/<vm_name>', methods=['POST'])
def power_start_vm(vm_name):

    try:
        validated_data = VMNameSchema().load({"vm_name":vm_name})
    except ValidationError as e:
        return jsonify({"error": f"{e}"}), 400

    try:
        #Check if vm exist
        vm = vmCollection.find_one({"name": vm_name }, {"_id": 0})
        if (not vm):
            return jsonify({"error": f"VM '{vm_name}' doesn't exist"}), 404
        
        vm_path = os.path.join(VM_PATH, vm_name)
        if not os.path.exists(vm_path):
            return jsonify({"error": f"VM '{vm_name}' folder doesn't exist"}), 404

        #Starting the vm
        v = vagrant.Vagrant(vm_path)
        v.up()
        return jsonify({"message": f"VM '{vm_name}' successfully started!"}), 200
    
    except pymongo.errors.ConnectionFailure as e:
        return jsonify({'error': 'Connection to database failed.'}), 500
    except Exception as e:
        return jsonify({"error": f"Error starting  vm. {e}"}), 500


@app.route('/vm/stop/<vm_name>', methods=['POST'])
def power_stop_vm(vm_name):

    try:
        validated_data = VMNameSchema().load({"vm_name":vm_name})
    except ValidationError as e:
        return jsonify({"error": f"{e}"}), 400

    try:
        #Check if vm exist
        vm = vmCollection.find_one({"name": vm_name }, {"_id": 0})
        if (not vm):
            return jsonify({"error": f"VM '{vm_name}' doesn't exist"}), 404
        
        vm_path = os.path.join(VM_PATH, vm_name)
        if not os.path.exists(vm_path):
            return jsonify({"error": f"VM '{vm_name}' folder doesn't exist"}), 404
        
        #Stopping the vm
        v = vagrant.Vagrant(vm_path)
        v.halt()
        return jsonify({"message": f"VM '{vm_name}' successfully stopped!"}), 200
    
    except pymongo.errors.ConnectionFailure as e:
        return jsonify({'error': 'Connection to database failed.'}), 500
    except Exception as e:
        return jsonify({"error": f"Error starting  vm. {e}"}), 500


@app.route('/vm/reload/<vm_name>', methods=['POST'])
def power_vm(vm_name):

    try:
        validated_data = VMNameSchema().load({"vm_name":vm_name})
    except ValidationError as e:
        return jsonify({"error": f"{e}"}), 400

    try:
        #Check if vm exist
        vm = vmCollection.find_one({"name": vm_name }, {"_id": 0})
        if (not vm):
            return jsonify({"error": f"VM '{vm_name}' doesn't exist"}), 404
        
        vm_path = os.path.join(VM_PATH, vm_name)
        if not os.path.exists(vm_path):
            return jsonify({"error": f"VM '{vm_name}' folder doesn't exist"}), 404

        #Reloading the vm
        v = vagrant.Vagrant(vm_path)
        v.reload()
        return jsonify({"message": f"VM '{vm_name}' successfully reloaded!"}), 201
    
    except pymongo.errors.ConnectionFailure as e:
        return jsonify({'error': 'Connection to database failed.'}), 500
    except Exception as e:
        return jsonify({"error": f"Error starting  vm. {e}"}), 500



@app.route('/services/priority', methods=['POST'])
def edit_service_priority():
    data = request.json

    try:
        validated_data = ServiceSchema().load(data)
    except ValidationError as e:
        return jsonify({"error": f"{e}"}), 400

    image = data.get ('image')
    service_port = data.get('service_port') 
    priority=data.get('priority')

    try:
        update_priority_service_list(image, service_port, priority, serviceCollection)
        return jsonify({'message': f"priority for service {service_port} in image {image} updated to {priority}"}), 200

    except ImageNotFound as e:
        return jsonify({"error": f"{e.message}"}), 404
    except ItemNotModified as e:
        return jsonify ({'message': f"{e.message}"}), 200
    except pymongo.errors.ConnectionFailure as e:
        return jsonify({'error': 'Connection to database failed.'}), 500
    except Exception as e:
        return jsonify({"error": f"Error. {e}"}), 500


@app.route('/services/list', methods=['GET'])
def service_list():

    try:
        serviceList = list(serviceCollection.find({} ,{"_id": 0}))
        return jsonify(serviceList), 200
    
    except pymongo.errors.ConnectionFailure as e:
        return jsonify({'error': 'Connection to database failed.'}), 500
    except Exception as e:
        return jsonify({"error": f"Error. {e}"}), 500



@app.route('/vm/ping', methods=['GET'])
def ping():
    return jsonify("server running"), 200


#Swagger docs api
SWAGGER_URL = '/apidocs'
API_DOCS_PATH = 'vm_docs.json'

swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    f'/{API_DOCS_PATH}',
    config={
        'app_name': "VM API Documentation"
    }
)
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)

#Request for documentation
@app.route(f'/{API_DOCS_PATH}')
def serve_swagger_file():
    return send_from_directory('.', API_DOCS_PATH)



if __name__ == '__main__':
    os.makedirs(VM_PATH, exist_ok=True)
    app.run(host=app.config['IP_ADDRESS'], port=app.config['PORT'])

    try:
        app.run(debug=True, use_reloader=False)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()


