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


# Método para crear una habitación
def create_room(id_home):
    # obtener la lista de habitaciones de un hogar
    home_rooms = get_home_rooms(id_home)
    
    # crear lista insertando las coincidencias del campo descripción 
    room_exists = list(filter(lambda desc: desc['description'] == request.json['description'], home_rooms))

    # comprobar si la habitación introducida existe. (se busca por el campo description)
    if len(room_exists) > 0:
        response = jsonify({'response': 'ERROR. The entered room already exists'})
        return response
    
    """ validar e insertar room """
    # obtener datos de la petición (datos json)
    data = request.json

    # validar si el contenido json es válido
    is_valid_room, msg = validate_json('schemas/schema_room.json', data)

    # si el contenido json no es válido, se muestra respuesta
    if is_valid_room == False:
        response = jsonify({
            'response': 'ERROR. The entered value is not valid',
            'message': msg})
        return response

    # Si la habitación no existe, se inserta en la lista de habitaciones
    db_home.update_one({'_id': ObjectId(id_home)}, {'$push': {'rooms': data}})

    response = jsonify(
        {
            'response': 'Room was created successfully',
            # 'message': msg,
            'new_room': data['description']
        })
    return response


# Método para obtener las habitaciones
def get_all_rooms(id_home):
    # obtener la lista de habitaciones de un hogar
    home_rooms = get_home_rooms(id_home)
    
    # convertir los datos anteriores, de bson a json
    response = json_util.dumps(home_rooms)
    # enviar datos convertidos al cliente
    return Response(response, mimetype='application/json')


# Método para obtener una habitación
def get_one_room(id_home):
    # obtener la lista de habitaciones de un hogar
    home_rooms = get_home_rooms(id_home)
    
    # obtener datos de la petición (datos json)
    data = request.json

    # validar si el contenido json es válido
    is_valid_room, msg = validate_json('schemas/schema_room_by_desc.json', data)

    # si el contenido json no es válido, se muestra respuesta
    if is_valid_room == False:
        response = jsonify({
            'response': 'ERROR. The entered value is not valid',
            'message': msg})
        return response

    # crear lista insertando las coincidencias del campo descripción 
    room_exists = list(filter(lambda desc: desc['description'] == request.json['description'], home_rooms))

    # Si la búsqueda tiene un solo resultado...
    if len(room_exists) == 1:
        # Se guarda ese resultado y se muestra
        response = jsonify(room_exists[0])
        return response
    else:
        response = jsonify(
            {
                'response': 'ERROR. Room not found',
                # 'message': msg,
                'room': data['description']
            })
        return response


# Método auxiliar para obtener la lista de habitaciones de un hogar, a través del id pasado por parámetro
def get_home_rooms(id_home):
    """ validar home """
    # se comprueba si el id introducido es válido
    is_valid_id = bson.ObjectId.is_valid(id_home)

    # si el id introducido no es válido se muestra mensaje de error
    if not is_valid_id:
        response = jsonify({'response': 'ERROR. The entered id is not valid.'})
        return response

    # obtener diccionario 'home' de mongodb (formato bson originalmente)
    home = db_home.find_one({'_id': ObjectId(id_home)})
    
    # comprobar si el id pasado por parámetro coincide con algún hogar de la base de datos
    if home == None:
        response = jsonify({'response': 'ERROR. The entered id does not exist.'})
        return response
    
    # devolver lista de diccionarios 'rooms'
    return home["rooms"]


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


# # Método para eliminar un hogar
# def delete_home(id):
#     db_home.delete_one({'_id': ObjectId(id)})
#     response = jsonify({'response': 'Home (' + id + ') was deleted successfully'})
#     return response


# # Método para actualizar un hogar
# def update_home(id):
#     # obtener datos de la petición (datos json)
#     data = request.json

#     # validar si el contenido json es válido
#     is_valid, msg = validate_home_json(data)

#     # comprobar si el hogar introducido existe. (se busca por el campo description)
#     home_exists = db_home.find_one({'description': request.json['description']})

#     # Si el hogar existe (se ha obtenido algún hogar en la búsqueda)...
#     if home_exists != None:
#         response = jsonify({'response': 'ERROR. The home introduced already exists'})
#     # Si el hogar no existe...
#     else:
#         if is_valid:
#             db_home.update_one({'_id': ObjectId(id)}, {'$set': data})

#             response = jsonify(
#                 {
#                     'response': 'Home (' + id + ') was updated successfully',
#                     'message': msg
#                 })
#         else:
#             response = jsonify(
#                 {
#                     'response': 'ERROR. The value entered is not valid',
#                     'message': msg
#                 })
#     return response
