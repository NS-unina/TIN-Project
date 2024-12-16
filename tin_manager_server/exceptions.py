import requests

class ContainerListError(Exception):
    def __init__(self, message, error_code=None):
        self.message = message
        self.error_code = error_code
        super().__init__(message)

class VmListError(Exception):
    def __init__(self, message, error_code=None):
        self.message = message
        self.error_code = error_code
        super().__init__(message) 


class ServerNotRunning(requests.exceptions.ConnectionError):
    def __init__(self, message, error_code=None):
        self.message = message
        self.error_code = error_code
        super().__init__(message) 


class CreateVmFailed(requests.exceptions.ConnectionError):
    def __init__(self, message, error_code=None):
        self.message = message
        self.error_code = error_code
        super().__init__(message)

class CreateContainerFailed(requests.exceptions.ConnectionError):
    def __init__(self, message, error_code=None):
        self.message = message
        self.error_code = error_code
        super().__init__(message)

