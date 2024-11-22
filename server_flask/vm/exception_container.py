class ContainerFileNotFound(FileNotFoundError):
    def __init__(self, message, error_code=None):
        self.message = message
        self.error_code = error_code
        super().__init__(message)