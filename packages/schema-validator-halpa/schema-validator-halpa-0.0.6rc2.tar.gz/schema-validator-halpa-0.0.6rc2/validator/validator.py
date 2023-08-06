import json
from os import path
from os.path import dirname, join
import os

from jsonschema import Draft7Validator, ErrorTree, FormatChecker, RefResolver
from jsonschema import validate as jsonschema_validate
from jsonschema.exceptions import ErrorTree, SchemaError
from jsonschema.exceptions import _Error as Error

from .exception import ValidationException


def load_validator(schema):
    """ Validates JSON schema (Draft 7 Validator)
        Raises SchemaError if schema check shows errors in schema
    """
    # Instantiate the Draft 7 Validator with format checker
    validator = Draft7Validator(schema=schema, format_checker=FormatChecker())
    try:
        validator.check_schema(schema)
        return validator
    except SchemaError as schema_error:
        raise ValidationException(schema=schema, message=schema_error.message)


def validate(schema, data):
    """ Validates JSON schema (Draft 7 Validator) and tests data (dictionary) against it\n
        Returns True if schema and data is valid, raises ValidationException if not
    """

    errors = {}

    # If schema is a file
    try:
        if type(schema) is not dict:
            schema = _load_json_file(schema)
    except FileNotFoundError as file_not_found:
        raise ValidationException(schema=schema, data=data, message="Schema file does not exist")

    try:
        validator = load_validator(schema)
    except SchemaError as schema_error:
        raise ValidationException(schema=schema, data=data, message=schema_error.message)

    # Check that data is a dictionary
    if type(data) is not dict:
        raise ValidationException(schema=schema, data=data, message="Data is not a dictionary")


    # Check required fields
    try:
        validator.validate(instance=data)
    except Error as validate_errors:
        errors["fields"] = {}
        # if any required field is missing
        if validate_errors.validator == "required":
            # check all fields
            for required in schema["required"]:
                if required not in data:
                    errors["fields"][required] = required + " is required"


    # Build error tree
    tree = ErrorTree(validator.iter_errors(instance=data))
    if tree.total_errors > 0:
        for errorItem in tree:
            for requirementType in tree[errorItem].errors:
                errors["fields"][errorItem] = tree[errorItem].errors[requirementType].message
    if not validator.is_valid(instance=data):
        raise ValidationException(schema=schema, data=data, message="Data could not be validated", errors=errors)

    return True

# https://medium.com/grammofy/testing-your-python-api-app-with-json-schema-52677fe73351
# Modified by Halpdesk

def is_valid(schema, data):
    """ Just checks validity. Gives no errors.
        Raises errors if schema can not be loaded
        Returns True if schema is valid, False otherwise
    """

    if type(schema) is not dict:
        schema = _load_json_file(schema)

    load_validator(schema)

    validation = validate(schema, data)
    
    return True

def _load_json_file(filename):
    """ Loads schema from an existing file 
        If PY_SCHEMA_PATH environment envirable is set, 
        schemas will be loaded relatively from there
    """

    schema_path = os.environ.get("PY_SCHEMA_PATH", "")

    fullpath = os.path.join(os.path.dirname(schema_path + "/"), filename) if schema_path else filename

    if not path.exists(fullpath):
        raise ValidationException(message=fullpath + " does not exist")

    with open(fullpath) as schema_file:
        return json.loads(schema_file.read())
