from .. import is_valid, require, validate as base_validate
import os

def validate(schema={}, required=[]):
    def decorator(inner_function):
        def validate_f(*args, **kwargs):

            data_parameter = os.environ.get("SCHEMA_VALIDATOR_DATA_PARAMETER", None)
            data = args[0].get(data_parameter) if data_parameter else args[0]

            if len(required) > 0 and not schema:
                require(required, data)
            else:
                base_validate(schema, data, required=required)
            # return function if validation passed
            return inner_function(*args, **kwargs)
        return validate_f
    return decorator
