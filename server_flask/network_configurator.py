from function_server import *
import subprocess

app = Flask(__name__)
app.config.from_object(__name__)

@app.route('/network/init_int', methods=['GET'])
def init_int():
    global vm_id_dictionary

    #Read from id_list already existing interfaces
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

    #Active those interfaces
    for values in vm_id_dictionary:

        veth_name = vm_id_dictionary.get(values)

        subprocess.run(["sudo", "ip", "link", "add", veth_name, "type", "veth", "peer", "name", f"{veth_name}-peer"], check=True)
        subprocess.run(["sudo", "ovs-vsctl", "add-port", ovs_bridge, veth_name], check=True)
        subprocess.run(["sudo", "ip", "link", "set", veth_name, "up"], check=True)
        subprocess.run(["sudo", "ip", "link", "set", f"{veth_name}-peer", "up"], check=True)

    return jsonify({'status': 'Network configured'}), 200


@app.route('/network/delete_global_int', methods=['GET'])
def delete_global_int():
    global vm_id_dictionary

    #Read from id_list already existing interfaces
    try:
        with open(os.path.join(VM_PATH, 'ID_LIST'), 'r') as id_list:
            vm_id_dictionary = json.load(id_list)
    except FileNotFoundError:
        return jsonify({"Nothing to delete"}), 200
    except json.JSONDecodeError as err:
        print (err)
    
    print (vm_id_dictionary)

    #Active those interfaces
    for values in vm_id_dictionary:

        veth_name = vm_id_dictionary.get(values)
        print (veth_name)
        
        subprocess.run(["sudo", "ovs-vsctl", "del-port", ovs_bridge, veth_name], check=True)
        subprocess.run(["sudo", "ip", "link", "delete", veth_name], check=True)

    return jsonify({'status': 'Network configured'}), 200




@app.route('/network/create_int/<vm_id>', methods=['POST'])
def create_int(vm_id):
    
    #Check if vm exist
    # vm_path = os.path.join(VM_PATH, vm_id)
    # if not os.path.exists(vm_path):
    #     return jsonify({"error": f"VM '{vm_id}' doesn't exist"}), 404

    #Interface name
    veth_name = f"veth-{vm_id}"


    try:
        #check if OVS exists, if not creates it
        if(not os.path.exists(f"/sys/class/net/{ovs_bridge}")):
            subprocess.run(["sudo", "ovs-vsctl", "add-br", ovs_bridge], check=True)
            print(f"Created OVS {ovs_bridge}")

        #check if veth already exists
        if(os.path.exists(f"/sys/class/net/{veth_name}")):
            return jsonify('error, the interface already exists'), 500


        subprocess.run(["sudo", "ip", "link", "add", veth_name, "type", "veth", "peer", "name", f"{veth_name}-peer"], check=True)
        subprocess.run(["sudo", "ovs-vsctl", "add-port", ovs_bridge, veth_name], check=True)
        subprocess.run(["sudo", "ip", "link", "set", veth_name, "up"], check=True)
        subprocess.run(["sudo", "ip", "link", "set", f"{veth_name}-peer", "up"], check=True)

        return jsonify({'status': 'Network configured', 'interface': f'{veth_name}-peer'}), 200

    except subprocess.CalledProcessError as e:
        return jsonify({'error': str(e)}), 500



@app.route('/network/delete_int/<vm_id>', methods=['DELETE'])
def delete_int(vm_id):
    
    #Check if vm exist
    # vm_path = os.path.join(VM_PATH, vm_id)
    # if not os.path.exists(vm_path):
    #     return jsonify({"error": f"VM '{vm_id}' doesn't exist"}), 404
    
    #Interface name
    veth_name = f"veth-{vm_id}"

    try:
        #check if OVS exists, if not creates it
        if(not os.path.exists(f"/sys/class/net/{ovs_bridge}")):
            return jsonify('error, the OVS does not exists'), 500

        #check if veth exists
        if(not os.path.exists(f"/sys/class/net/{veth_name}")):
            return jsonify(f'error, the interface {veth_name} does not exists'), 500

        subprocess.run(["sudo", "ovs-vsctl", "del-port", ovs_bridge, veth_name], check=True)
        subprocess.run(["sudo", "ip", "link", "delete", veth_name], check=True)

        return jsonify({'status': 'Network interface deleted', 'interface deleted': f'{veth_name}-peer'}), 200

    except subprocess.CalledProcessError as e:
        return jsonify({'error': str(e)}), 500



if __name__ == '__main__':
    app.run(port=5001)

