class Config:
    IP_ADDRESS = '127.0.0.1'  # Default to localhost
    PORT = 5002  # Default Flask port
    DEBUG = True  # Enable debug mode
    ENV = 'development'  # Can be 'development', 'testing', or 'production'

    DATABASE_CONNECTION = "mongodb://10.1.3.1:27017/"

    VM_SERVER_IP="127.0.0.1" #Ip Address for vm configurator server
    VM_SERVER_PORT="5000" #Port for vm configurator server

class ProductionConfig(Config):
    DEBUG = False
    ENV = 'production'

class DevelopmentConfig(Config):
    DEBUG = True
    ENV = 'development'
