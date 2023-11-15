from flask import Flask, request, jsonify
import logging

app = Flask(__name__)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
        # logging.FileHandler('my_log.log')
    ]
)

logger = logging.getLogger(__name__)

service_registry = {}

@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'

@app.route('/register', methods =['POST'])
def register_service():
    data=request.get_json()
    service_name = data.get('name')
    service_port = data.get('port')
    service_address = data.get('host')
    service_registry[service_name] = data
    logger.info(f"Service with name {service_name} and port {service_port} and address {service_address} has "
                f"registered "
                f"successfully")
    return jsonify({"message": "Service registered successfully"}), 200

@app.route('/deregister/<string:service_name>', methods=['DELETE'])
def deregister_service(service_name):
    if service_name in service_registry:
        logger.info(f"Service with name {service_name} is being deregistered")
        del service_registry[service_name]
        return jsonify({"message": "Service deregistered successfully"}), 200
        return jsonify ({"message": "Service not found"}), 404

@app.route('/get_info/<string:service_name>', methods =['GET'])
def get_service_info(service_name):
    logger.info(f"Service registry contains: {service_registry}")
    if service_name in service_registry:
        service_info = service_registry[service_name]
        logger.info(f"Sent service info back : {service_info}")
        return jsonify(service_info), 200
    else:
        return ({"message": "Service not found"}), 404

@app.route('/status', methods=['GET'])
def service_discovery_status():
    return jsonify({"status": "Service Discovery is running"})


if __name__ == '__main__':
    app.run(debug=True, port=8001, host='127.0.0.1')
