from flask import Flask, jsonify, request, send_from_directory
import requests
import json
from flask_swagger_ui import get_swaggerui_blueprint


app = Flask (__name__)
app.config.from_object(__name__)



#@app.route('/controller/...', methods=['POST'])












#Swagger docs api
SWAGGER_URL = '/apidocs'
API_DOCS_PATH = 'network_docs.json'

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
    app.run(port=5003)