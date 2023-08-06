from .. import is_valid, require, validate as base_validate

def validate(schema={}, data={}, required=[]):
    def decorator(f):
        def validate_f(*args, **kwargs):
            if len(required) > 0 and not schema:
                return require(required, data)
            else:
                return base_validate(schema, data)
        return validate_f
    return decorator
