from flask import Flask, request, jsonify
import subprocess
import os

app = Flask(__name__)
app.config.from_object(__name__)

#Directory for vms
VM_PATH = './vm'
#OVS 
ovs_bridge = "br0"

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

