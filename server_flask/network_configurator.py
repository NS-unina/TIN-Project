from function_server import *
import subprocess


app = Flask(__name__)
app.config.from_object(__name__)

ip_host = "10.1.3.1/24"


@app.route('/network/create_int/<vm_id>', methods=['POST'])
def create_int(vm_id):

    #Interface name
    veth_name = f"veth-{vm_id}"

    try:
        #check if OVS exists, if not creates it
        if(not os.path.exists(f"/sys/class/net/{ovs_bridge}")):
            subprocess.run(["sudo", "ovs-vsctl", "add-br", ovs_bridge], check=True)
            if(os.path.exists(f"/sys/class/net/{veth_name}")):
                subprocess.run(["sudo", "ovs-vsctl", "add-port", ovs_bridge, veth_name], check=True)
            #connect bridge to host
            subprocess.run(["sudo", "ovs-vsctl", "add-port", ovs_bridge, "host-veth", "--", "set", "interface", "host-veth", "type=internal"], check=True)
            subprocess.run(["sudo", "ip", "addr", "add", ip_host, "dev", "host-veth"], check=True)
            subprocess.run(["sudo", "ip", "link", "set", "host-veth", "up"], check=True)
            print(f"Created OVS {ovs_bridge}")

        #check if veth already exists
        if(os.path.exists(f"/sys/class/net/{veth_name}")):
            #check if down
            state = subprocess.check_output(["ip", "link", "show", veth_name], text=True)
            if ("state DOWN" in state):
                subprocess.run(["sudo", "ip", "link", "set", veth_name, "up"], check=True)
                subprocess.run(["sudo", "ip", "link", "set", f"{veth_name}-peer", "up"], check=True)
                return jsonify({'status': 'Interface already exists and it was turned on.', 'interface': f'{veth_name}-peer'}), 200
            return jsonify({'status': 'Interface already exists and it is already up.', 'interface': f'{veth_name}-peer'}), 200
        
        subprocess.run(["sudo", "ip", "link", "add", veth_name, "type", "veth", "peer", "name", f"{veth_name}-peer"], check=True)
        
        if not (f"Port {veth_name}" in (subprocess.check_output(["sudo", "ovs-vsctl", "show"], text=True))):
            subprocess.run(["sudo", "ovs-vsctl", "add-port", ovs_bridge, veth_name], check=True)
        
        subprocess.run(["sudo", "ip", "link", "set", veth_name, "up"], check=True)
        subprocess.run(["sudo", "ip", "link", "set", f"{veth_name}-peer", "up"], check=True)

        return jsonify({'status': 'Network configured', 'interface': f'{veth_name}-peer'}), 201
    except subprocess.CalledProcessError as e:
        return jsonify({'error': str(e)}), 500



@app.route('/network/delete_int/<vm_id>', methods=['DELETE'])
def delete_int(vm_id):
    
    #Interface name
    veth_name = f"veth-{vm_id}"

    try:
        #check if OVS exists, if not creates it
        if(not os.path.exists(f"/sys/class/net/{ovs_bridge}")):
            return jsonify('error, the OVS does not exists'), 500

        #check if veth exists
        if(not os.path.exists(f"/sys/class/net/{veth_name}")):
            return jsonify(f'error, the interface {veth_name} does not exists'), 500

        if (f"Port {veth_name}" in (subprocess.check_output(["sudo", "ovs-vsctl", "show"], text=True))):
            subprocess.run(["sudo", "ovs-vsctl", "del-port", ovs_bridge, veth_name], check=True)
        
        subprocess.run(["sudo", "ip", "link", "delete", veth_name], check=True)

        return jsonify({'status': 'Network interface deleted', 'interface deleted': f'{veth_name}-peer'}), 200

    except subprocess.CalledProcessError as e:
        return jsonify({'error': str(e)}), 500



@app.route('/network/ping', methods=['GET'])
def ping():
    return jsonify("server running"), 200



if __name__ == '__main__':
    app.run(port=5001)
    

