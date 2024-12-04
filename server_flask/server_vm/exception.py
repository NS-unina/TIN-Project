class VagrantfileNotFound(FileNotFoundError):
    def __init__(self, message, error_code=None):
        self.message = message
        self.error_code = error_code
        super().__init__(message) 


class VM_listFileNotFound(FileNotFoundError):
    def __init__(self, message, error_code=None):
        self.message = message
        self.error_code = error_code
        super().__init__(message)

class VmNotFound(FileNotFoundError):
    def __init__(self, message, error_code=None):
        self.message = message
        self.error_code = error_code
        super().__init__(message)

class FieldNotValid(Exception):
    def __init__(self, message, error_code=None):
        self.message = message
        self.error_code = error_code
        super().__init__(message)

class DefaultIpNotAvailable(Exception):
    def __init__(self, message, error_code=None):
        self.message = message
        self.error_code = error_code
        super().__init__(message)
        