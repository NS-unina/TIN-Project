class Config:
    IP_ADDRESS = '127.0.0.1'  # Default to localhost
    PORT = 5003  # Default Flask port
    DEBUG = True  # Enable debug mode
    ENV = 'development'  # Can be 'development', 'testing', or 'production'

    
    VM_SERVER="http://127.0.0.1:5000" #ip Address for vm configurator server
    PORT_CONTAINER_SERVER="5002" #port for container configurator server

    MAX_CONTAINERS=5

class ProductionConfig(Config):
    DEBUG = False
    ENV = 'production'

class DevelopmentConfig(Config):
    DEBUG = True
    ENV = 'development'
