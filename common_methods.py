from pymongo import MongoClient

import json
import jsonschema
from jsonschema import validate


# Método que genera la conexión con el servidor mongo
def link_server():
    # Conexión a servidor MongoDB
    client = MongoClient(
        host='192.168.1.220:27017',  # <-- IP and port go here
        serverSelectionTimeoutMS=3000,  # 3 second timeout
        username="kirkdax",
        password="b*jEeJfM7T*y!X",
    )
    return client


# Método auxiliar para validar un schema (POST y PUT)
def validate_json(urlfile, json_data):
    """This function loads the given schema available"""
    with open(urlfile, 'r') as file:
        schema = json.load(file)
    
    """REF: https://json-schema.org/ """
    # Describe what kind of json you expect.
    execute_api_schema = schema

    try:
        validate(instance=json_data, schema=execute_api_schema)
    except jsonschema.exceptions.ValidationError as err:
        print(err)
        err = "Given JSON data is InValid"
        return False, err

    message = "Given JSON data is Valid"
    return True, message