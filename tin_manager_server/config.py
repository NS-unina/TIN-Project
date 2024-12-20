class Config:
    IP_ADDRESS = '127.0.0.1'  # Default to localhost
    PORT = 5003  # Default Flask port
    DEBUG = True  # Enable debug mode
    ENV = 'development'  # Can be 'development', 'testing', or 'production'

    
    VM_SERVER_IP='127.0.0.1' #ip Address for vm configurator server
    VM_SERVER_PORT='5000'

    CONTAINER_SERVER_PORT='5002' #port for container configurator server

    MAX_CONTAINERS=5

class ProductionConfig(Config):
    DEBUG = False
    ENV = 'production'

class DevelopmentConfig(Config):
    DEBUG = True
    ENV = 'development'
