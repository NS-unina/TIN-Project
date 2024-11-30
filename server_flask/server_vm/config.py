class Config:
    IP_ADDRESS = '127.0.0.1'  # Default to localhost
    PORT = 5000  # Default Flask port
    DEBUG = True  # Enable debug mode
    ENV = 'development'  # Can be 'development', 'testing', or 'production'

    VM_PATH = '../vm' #Directory for vms
    NET_SERVER="http://127.0.0.1:5001" #ip Address for network configurator server



class ProductionConfig(Config):
    DEBUG = False
    ENV = 'production'

class DevelopmentConfig(Config):
    DEBUG = True
    ENV = 'development'
