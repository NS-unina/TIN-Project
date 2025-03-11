class Config:
    IP_ADDRESS = '127.0.0.1'  # Default to localhost
    PORT = 5002  # Default Flask port
    DEBUG = True  # Enable debug mode
    ENV = 'development'  # Can be 'development', 'testing', or 'production'

    DATABASE_IP = "0.0.0.0"
    DATABASE_PORT = "27017"

class ProductionConfig(Config):
    DEBUG = False
    ENV = 'production'

class DevelopmentConfig(Config):
    DEBUG = True
    ENV = 'development'
