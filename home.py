from flask import jsonify, request, Response

import bson
from bson import json_util
from bson.objectid import ObjectId
from pymongo import MongoClient

import json
import jsonschema
from jsonschema import validate

# Conexión a servidor MongoDB
client = MongoClient(
    host='localhost:27017',  # <-- IP and port go here
    serverSelectionTimeoutMS=3000,  # 3 second timeout
    username="test",
    password="test",
)
# client = MongoClient('mongodb://test:test@127.0.0.1:27017/test?authSource=admin&readPreference=primary&appname=MongoDB%20Compass&ssl=false')


# Conexión a la base de datos
db = client["organi"]

# Variable para definir un acceso directo al documento de hogares (home)
db_home = db.home


# Método para crear un hogar
def create_home():
    # obtener datos de la petición (datos json)
    data = request.json

    # validar si el contenido json es válido
    is_valid, msg = validate_home_json(data)

    # si el contenido json no es válido, se muestra respuesta
    if is_valid == False:
        response = jsonify({
            'response': 'ERROR. The value entered is not valid',
            'message': msg})
        return response

    # comprobar si el hogar introducido existe. (se busca por el campo description)
    home_exists = db_home.find_one({'description': request.json['description']})

    # Si el hogar existe (se ha obtenido algún hogar en la búsqueda)...
    if home_exists != None:
        response = jsonify({'response': 'ERROR. The home introduced already exists'})
        return response
        
    # Si el hogar no existe, se inserta hogar y se almacena id
    home_id = str(db_home.insert_one(data).inserted_id)

    response = jsonify(
        {
            'response': 'Home was created successfully',
            # 'message': msg,
            'new_home': home_id
        })
    return response


def get_home_schema():
    """This function loads the given schema available"""
    with open('schemas/schema_home.json', 'r') as file:
        schema = json.load(file)
    return schema

def validate_home_json(json_data):
    """REF: https://json-schema.org/ """
    # Describe what kind of json you expect.
    execute_api_schema = get_home_schema()

    try:
        validate(instance=json_data, schema=execute_api_schema)
    except jsonschema.exceptions.ValidationError as err:
        print(err)
        err = "Given JSON data is InValid"
        return False, err

    message = "Given JSON data is Valid"
    return True, message


# Método para obtener los hogares
def get_homes():
    # obtener datos de mongodb (formato bson originalmente)
    homes = db_home.find()
    # convertir los datos anteriores, de bson a json
    response = json_util.dumps(homes)
    # enviar datos convertidos al cliente
    return Response(response, mimetype='application/json')


# Método para obtener un hogar
def get_home_by_id(id):
    # se comprueba si el id introducido es válido
    is_valid_id = bson.ObjectId.is_valid(id)

    # si el id introducido no es válido se muestra mensaje de error
    if not is_valid_id:
        response = jsonify({'response': 'ERROR. the entered id is not valid.'})
        return response
        
    # obtener datos de mongodb (formato bson originalmente)
    home = db_home.find_one({'_id': ObjectId(id)})

    if home == None:
        response = jsonify({'response': 'ERROR. the entered id does not exist.'})
        return response
    else:
        # convertir los datos anteriores, de bson a json
        response = json_util.dumps(home)
        # se devuelve la respuesta en formato json
        return Response(response, mimetype='application/json')


# Método para obtener un hogar filtrando por descripción
def get_homes_by_description():
    # obtener datos de la petición (datos json)
    data = request.json

    # comprobar si se han introducido datos (body json)
    if data == None:
        response = jsonify({'response': 'ERROR. no value has been entered.'})
        return response

    # validar si el contenido json es válido
    is_valid, msg = validate_home_json(data)

    # si el contenido json no es válido, se muestra respuesta
    if is_valid == False:
        response = jsonify({
            'response': 'ERROR. The value entered is not valid',
            'message': msg})
        return response

    # filtro para buscar coincidencias en el campo 'description'
    filter = {'description': {'$regex': request.json['description']}}

    # se realiza la búsqueda con el filtro anterior
    query = db_home.find(filter=filter)

    # convertir los datos anteriores, de bson a json
    response = json_util.dumps(query)

    # se devuelve la respuesta en formato json
    return Response(response, mimetype='application/json')


# Método para eliminar un hogar
def delete_home(id):
    db_home.delete_one({'_id': ObjectId(id)})
    response = jsonify({'response': 'Home (' + id + ') was deleted successfully'})
    return response


# Método para actualizar un hogar
def update_home(id):
    # obtener datos de la petición (datos json)
    data = request.json

    # validar si el contenido json es válido
    is_valid, msg = validate_home_json(data)

    # comprobar si el hogar introducido existe. (se busca por el campo description)
    home_exists = db_home.find_one({'description': request.json['description']})

    # Si el hogar existe (se ha obtenido algún hogar en la búsqueda)...
    if home_exists != None:
        response = jsonify({'response': 'ERROR. The home introduced already exists'})
    # Si el hogar no existe...
    else:
        if is_valid:
            db_home.update_one({'_id': ObjectId(id)}, {'$set': data})

            response = jsonify(
                {
                    'response': 'Home (' + id + ') was updated successfully',
                    'message': msg
                })
        else:
            response = jsonify(
                {
                    'response': 'ERROR. The value entered is not valid',
                    'message': msg
                })
    return response