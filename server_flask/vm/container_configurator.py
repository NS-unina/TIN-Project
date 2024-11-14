from flask import Flask, jsonify, request
import subprocess
import docker

app = Flask(__name__)
client = docker.from_env()


@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/create', methods=['POST'])
def create_container():
    data = request.json
    name = data.get('name')
    docker_image = data.get('image')
    vm_port = data.get('port')

    if not docker_image:
        return jsonify({"error": "Image field is needed"}), 400
    if not vm_port:
        return jsonify({"error": "Port field is needed"}), 400
    if not name:
        return jsonify({"error": "Name field is needed"}), 400
    
    
    client.containers.run(docker_image,name=name, detach=True, ports={vm_port: 2222})
    return jsonify({"message": f"Container '{name}' successfully created!"}), 201


@app.route('/delete/<nome_container>', methods=['DELETE'])



@app.route('/cowrie')
def deploy_cowrie():
    try:
        result = subprocess.run(['docker', 'pull', 'cowrie/cowrie'], capture_output=True, text=True, check=True)
        return jsonify({"status": "success", "output": result.stdout}), 200
    except subprocess.CalledProcessError as e:
        return jsonify({"status": "error", "error": e.stderr}), 500


