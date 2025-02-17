class Config:
    IP_ADDRESS = '127.0.0.1'  # Default to localhost
    PORT = 5001  # Default to 5001
    DEBUG = True  # Enable debug mode
    ENV = 'development'  # Can be 'development' or 'production'

    IP_HOST = "10.1.3.1/24" #IP of the host machine on which to create the 'host-veth'
    IP_ONOS = "127.0.0.1" # IP of the SDN Controller
    PORT_ONOS = "6653" # Port of the SDN Controller
    OVS_BRIDGE = "br0" # The name of the OVS bridge that will be created 

class ProductionConfig(Config):
    DEBUG = False
    ENV = 'production'

class DevelopmentConfig(Config):
    DEBUG = True
    ENV = 'development'
