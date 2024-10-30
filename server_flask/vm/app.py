from flask import Flask, jsonify
import subprocess

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/cowrie')
def deploy_cowrie():
    try:
        result = subprocess.run(['docker', 'pull', 'cowrie/cowrie'], capture_output=True, text=True, check=True)
        return jsonify({"status": "success", "output": result.stdout}), 200
    except subprocess.CalledProcessError as e:
        return jsonify({"status": "error", "error": e.stderr}), 500


