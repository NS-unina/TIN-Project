class Config:
    IP_ADDRESS = '127.0.0.1'  # Default to localhost
    PORT = 5003  # Default Flask port
    DEBUG = True  # Enable debug mode
    ENV = 'development'  # Can be 'development', 'testing', or 'production'

    
    VM_SERVER_IP='192.168.1.32' #ip Address for vm configurator server
    VM_SERVER_PORT='5000'

    CONTAINER_SERVER_PORT='5002' #port for container configurator server

    MAX_CONTAINERS=10
    UTILIZATION_LIMIT=85 # % limit for total vm capacity. after the limit is surpassed new vms will be created

    ONOS_IP='127.0.0.1' #ip address for onos
    ONOS_PORT='8181'

    ONOS_AUTH_USERNAME = "onos"
    ONOS_AUTH_PASSWORD = "rocks"

class ProductionConfig(Config):
    DEBUG = False
    ENV = 'production'

class DevelopmentConfig(Config):
    DEBUG = True
    ENV = 'development'
