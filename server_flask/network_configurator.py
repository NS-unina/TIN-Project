from flask import Flask, request, jsonify
import subprocess
import os

app = Flask(__name__)
app.config.from_object(__name__)

#Directory for vms
VM_PATH = './vm'


@app.route('/network/create_int/<vm_name>', methods=['POST'])
def create_int(vm_name):
    
    #Check if vm exist
    vm_path = os.path.join(VM_PATH, vm_name)
    if not os.path.exists(vm_path):
        return jsonify({"error": f"VM '{vm_name}' doesn't exist"}), 404

    # Nomi di interfacce e bridge per la configurazione della rete
    veth_name = f"veth-{vm_name}"
    ovs_bridge = "br0"


    try:
        #check se già esiste la veth
        subprocess.run(["sudo", "ip", "link", "add", veth_name, "type", "veth", "peer", "name", f"{veth_name}-peer"], check=True)
        subprocess.run(["sudo", "ovs-vsctl", "add-port", ovs_bridge, veth_name], check=True)
        subprocess.run(["sudo", "ip", "link", "set", veth_name, "up"], check=True)
        subprocess.run(["sudo", "ip", "link", "set", f"{veth_name}-peer", "up"], check=True)

        return jsonify({'status': 'Rete configurata'}), 200

    except subprocess.CalledProcessError as e:
        return jsonify({'error': str(e)}), 500



if __name__ == '__main__':
    app.run(port=5001)

