from flask import Flask, jsonify, send_from_directory
from flask_swagger_ui import get_swaggerui_blueprint
import subprocess
import os

from validation_schemas import *

from config import DevelopmentConfig


# ********[ LOAD CONFIGURATION FROM config.py ]********
app = Flask(__name__)
app.config.from_object(DevelopmentConfig)  # Load the configuration

IP_HOST = app.config['IP_HOST']
IP_ONOS = app.config['IP_ONOS']
PORT_ONOS = app.config['PORT_ONOS']
ovs_bridge = app.config['OVS_BRIDGE']


# ********[ STARTUP ]********
try:
    #checks if OVS exists, if not creates it
    if(not os.path.exists(f"/sys/class/net/{ovs_bridge}")):
        subprocess.run(["sudo", "ovs-vsctl", "add-br", ovs_bridge], check=True)
        print(f"Created OVS {ovs_bridge}")
    subprocess.run(["sudo", "ovs-vsctl", "set", "bridge", ovs_bridge, "protocols=OpenFlow13", "--", "set-controller", ovs_bridge, f"tcp:{IP_ONOS}:{PORT_ONOS}"], check=True)
    
    #connect bridge to host
    if(not os.path.exists(f"/sys/class/net/host-veth")):
        subprocess.run(["sudo", "ovs-vsctl", "add-port", ovs_bridge, "host-veth", "--", "set", "interface", "host-veth", "type=internal"], check=True)

    #checks if host-veth down
    state = subprocess.check_output(["ip", "link", "show", "host-veth"], text=True)
    if ("state DOWN" in state):
        subprocess.run(["sudo", "ip", "addr", "add", IP_HOST, "dev", "host-veth"], check=True)
        subprocess.run(["sudo", "ip", "link", "set", "host-veth", "up"], check=True)

    print ("\nSTARTUP DONE")

except Exception as e:
    print (f"error: {e}")


# ********[ API ]********
@app.route('/network/create_int/<veth_id>', methods=['POST'])
def create_int(veth_id):

    try:
        validated_data = VethIdSchema().load({"veth_id":veth_id})
    except ValidationError as e:
        return jsonify({"error": f"{e}"}), 400

    #Interface name
    veth_name = f"veth-{veth_id}"

    try:
        #check if OVS exists, if not creates it
        if(not os.path.exists(f"/sys/class/net/{ovs_bridge}")):
            subprocess.run(["sudo", "ovs-vsctl", "add-br", ovs_bridge], check=True)
            print(f"Created OVS {ovs_bridge}")
        subprocess.run(["sudo", "ovs-vsctl", "set", "bridge", ovs_bridge, "protocols=OpenFlow13", "--", "set-controller", ovs_bridge, f"tcp:{IP_ONOS}:{PORT_ONOS}"], check=True)

        # if veth doesn't exist
        if not (os.path.exists(f"/sys/class/net/{veth_name}")):
            subprocess.run(["sudo", "ip", "link", "add", veth_name, "type", "veth", "peer", "name", f"{veth_name}-peer"], check=True)

        # if not already in ovsbridge
        if (not veth_name in subprocess.check_output(["sudo", "ovs-vsctl", "show"], text=True)):
            subprocess.run(["sudo", "ovs-vsctl", "add-port", ovs_bridge, veth_name], check=True)

        # status UP
        subprocess.run(["sudo", "ip", "link", "set", f"{veth_name}-peer", "up"], check=True)
        subprocess.run(["sudo", "ip", "link", "set", veth_name, "up"], check=True)

        mac = subprocess.run(["cat", f"/sys/class/net/{veth_name}/address"], capture_output=True, text=True, check=True)
        return jsonify({'status': 'Network configured', 'interface': f'{veth_name}-peer','mac':mac.stdout.strip()}), 201

    except subprocess.CalledProcessError as e:
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        return jsonify({'error': e}), 500


@app.route('/network/delete_int/<veth_id>', methods=['DELETE'])
def delete_int(veth_id):
    
    try:
        validated_data = VethIdSchema().load({"veth_id":veth_id})
    except ValidationError as e:
        return jsonify({"error": f"{e}"}), 400    

    #Interface name
    veth_name = f"veth-{veth_id}"

    try:
        #Check if veth exists
        if(not os.path.exists(f"/sys/class/net/{veth_name}")):
            return jsonify({'error': f'The interface {veth_name} does not exists'}), 500
        
        #If bridge exists, delete the veth port
        if(os.path.exists(f"/sys/class/net/{ovs_bridge}")):
            if (f"Port {veth_name}" in (subprocess.check_output(["sudo", "ovs-vsctl", "show"], text=True))):
                subprocess.run(["sudo", "ovs-vsctl", "del-port", ovs_bridge, veth_name], check=True)
        
        subprocess.run(["sudo", "ip", "link", "delete", veth_name], check=True)
        return jsonify({'status': 'Network interface deleted', 'interface deleted': f'{veth_name}-peer'}), 200

    except subprocess.CalledProcessError as e:
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        return jsonify({'error': e}), 500



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
    

