from flask import Flask, jsonify, send_from_directory
from flask_swagger_ui import get_swaggerui_blueprint
import subprocess
import os
from config import DevelopmentConfig


app = Flask(__name__)
#app.config.from_object(__name__)
app.config.from_object(DevelopmentConfig)  # Load the configuration


ip_host = app.config['IP_HOST']
ip_onos = app.config['IP_ONOS']
ovs_bridge = app.config['OVS_BRIDGE']

try:
    #check if OVS exists, if not creates it
    if(not os.path.exists(f"/sys/class/net/{ovs_bridge}")):
        subprocess.run(["sudo", "ovs-vsctl", "add-br", ovs_bridge], check=True)
        #subprocess.run(["sudo", "ovs-vsctl", "set", "bridge", ovs_bridge, "protocols=OpenFlow10", "--", "set-controller", ovs_bridge, f"tcp:{ip_onos}:6653"], check=True)
        print(f"Created OVS {ovs_bridge}")
    #connect bridge to host
    if(not os.path.exists(f"/sys/class/net/host-veth")):
        subprocess.run(["sudo", "ovs-vsctl", "add-port", ovs_bridge, "host-veth", "--", "set", "interface", "host-veth", "type=internal"], check=True)
    
    #check if host-veth down
    state = subprocess.check_output(["ip", "link", "show", "host-veth"], text=True)
    if ("state DOWN" in state):
        subprocess.run(["sudo", "ip", "addr", "add", ip_host, "dev", "host-veth"], check=True)
        subprocess.run(["sudo", "ip", "link", "set", "host-veth", "up"], check=True)

except Exception as e:
    print (f"error: {e}")

@app.route('/network/create_int/<vm_id>', methods=['POST'])
def create_int(vm_id):

    #Interface name
    veth_name = f"veth-{vm_id}"

    try:
        #check if OVS exists, if not creates it
        if(not os.path.exists(f"/sys/class/net/{ovs_bridge}")):
            return jsonify({'error': 'Ovs does not exists'}), 404

        #check if veth already exists
        if(os.path.exists(f"/sys/class/net/{veth_name}")):
            ovs_connection = subprocess.check_output(["sudo", "ovs-vsctl", "show"], text=True)
            if (not veth_name in ovs_connection):
                subprocess.run(["sudo", "ovs-vsctl", "add-port", ovs_bridge, veth_name], check=True)
            #check if down
            state = subprocess.check_output(["ip", "link", "show", veth_name], text=True)
            if ("state DOWN" in state):
                subprocess.run(["sudo", "ip", "link", "set", veth_name, "up"], check=True)
                subprocess.run(["sudo", "ip", "link", "set", f"{veth_name}-peer", "up"], check=True)
            return jsonify({'status': 'Interface already exists and it is up.', 'interface': f'{veth_name}-peer'}), 200
        
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



#Swagger docs api
SWAGGER_URL = '/apidocs'
API_DOCS_PATH = 'network_docs.json'

swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    f'/{API_DOCS_PATH}',
    config={
        'app_name': "Network API Documentation"
    }
)
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)

#Request for documentation
@app.route(f'/{API_DOCS_PATH}')
def serve_swagger_file():
    return send_from_directory('.', API_DOCS_PATH)


if __name__ == '__main__':
    app.run(host=app.config['IP_ADDRESS'], port=app.config['PORT'])
    

