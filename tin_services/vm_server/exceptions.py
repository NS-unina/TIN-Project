import pymongo.errors

#Network Exceptions
class NetworkServerError(Exception):
    def __init__(self, message, error_code=None):
        self.message = message
        self.error_code = error_code
        super().__init__(message)

class DefaultIpNotAvailable(Exception):
    def __init__(self, message, error_code=None):
        self.message = message
        self.error_code = error_code
        super().__init__(message)
    

class VmNotFound(FileNotFoundError):
    def __init__(self, message, error_code=None):
        self.message = message
        self.error_code = error_code
        super().__init__(message)

class VagrantfileNotFound(FileNotFoundError):
    def __init__(self, message, error_code=None):
        self.message = message
        self.error_code = error_code
        super().__init__(message) 

#Mongo Exception
class MongoError(Exception):
    def __init__(self, message, error_code=None):
        self.message = message
        self.error_code = error_code
        super().__init__(message)

class ItemNotModified(MongoError):
    def __init__(self, message, error_code=None):
        self.message = message
        self.error_code = error_code
        super().__init__(message)

class ItemNotFound(MongoError):
    def __init__(self, message, error_code=None):
        self.message = message
        self.error_code = error_code
        super().__init__(message)

class ImageNotFound(MongoError):
    def __init__(self, message, error_code=None):
        self.message = message
        self.error_code = error_code
        super().__init__(message)

class FailedInsertion(MongoError):
    def __init__(self, message, error_code=None):
        self.message = message
        self.error_code = error_code
        super().__init__(message)

class DatabaseNotFound(MongoError):
    def __init__(self, message, error_code=None):
        self.message = message
        self.error_code = error_code
        super().__init__(message)

class CollectionNotFound(MongoError):
    def __init__(self, message, error_code=None):
        self.message = message
        self.error_code = error_code
        super().__init__(message)


















        