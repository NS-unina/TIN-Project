class Config:
    IP_ADDRESS = '127.0.0.1'  # Default to localhost
    PORT = 5000  # Default Flask port
    DEBUG = True  # Enable debug mode
    ENV = 'development'  # Can be 'development', 'testing', or 'production'

    VM_PATH = '../vm' #Directory for vms
    DATABASE_IP = "0.0.0.0"
    DATABASE_PORT = "27017"

    NET_SERVER_IP="127.0.0.1" #ip Address for network configurator server
    NET_SERVER_PORT="5001" #Port for network configurator server
    DEFAULT_NETWORK = "10.1.3.0/24"
    EXCLUDED_ADDRESSES = ["10.1.3.1"]


class ProductionConfig(Config):
    DEBUG = False
    ENV = 'production'

class DevelopmentConfig(Config):
    DEBUG = True
    ENV = 'development'
