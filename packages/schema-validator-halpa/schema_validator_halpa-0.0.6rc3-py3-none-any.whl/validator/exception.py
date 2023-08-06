
class ValidationException(RuntimeError):
    def __init__(self, schema={}, data={}, message="", errors={}):
        self.schema = schema
        self.data = data
        self.message = message
        self.errors = errors

    def __str__(self):
        return self.message
