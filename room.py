from flask import jsonify, request, Response

import bson
from bson import json_util
from bson.objectid import ObjectId
from pymongo import MongoClient

import json
import jsonschema
from jsonschema import validate

from common_methods import *


# Conexión al servidor MongoDB
client = link_server()

# Conexión a la base de datos
db = client["organi"]

# Variable para definir un acceso directo al documento de hogares (home)
db_room = db.room


# Método para crear una habitación
def create_room(id_home):
    """ comprobar id_home """
    # se comprueba si el id introducido es válido
    is_valid_id = bson.ObjectId.is_valid(id_home)

    # si el id introducido no es válido se muestra mensaje de error
    if not is_valid_id:
        response = jsonify({'response': 'ERROR. The entered id is not valid.'})
        return response

    # obtener diccionario 'home' de mongodb (formato bson originalmente)
    home = db.home.find_one({'_id': ObjectId(id_home)})
    
    # comprobar si el id pasado por parámetro coincide con algún hogar de la base de datos
    if home == None:
        response = jsonify({'response': 'ERROR. The entered id does not exist.'})
        return response

    """ insertar habitación """
    # obtener datos de la petición (datos json)
    data = request.json

    # validar si el contenido json es válido
    is_valid, msg = validate_json('schemas/schema_room.json', data)

    # si el contenido json no es válido, se muestra respuesta
    if is_valid == False:
        response = jsonify({
            'response': 'ERROR. The value entered is not valid',
            'message': msg})
        return response

    # comprobar si la habitación introducida existe. (se busca por el campo description)
    room_exists = db_room.find_one({'description': request.json['description']})

    # Si la habitación existe (se ha obtenido alguna habitación en la búsqueda)...
    if room_exists != None:
        response = jsonify({'response': 'ERROR. The entered room already exists'})
        return response

    # agregar relación id_home en habitación
    data["id_home"] = ObjectId(id_home)

    # Si la habitación no existe, se inserta la habitación y se almacena id
    room_id = str(db_room.insert_one(data).inserted_id)

    response = jsonify(
        {
            'response': 'Room was created successfully',
            # 'message': msg,
            'new_room': room_id
        })
    return response
    

# Método para obtener las habitaciones con su hogar correspondiente
def get_room_with_home():
    # parámetros para aggregate
    pipeline = [{'$lookup':
                    {
                        'from': "home",
                        'localField': "id_home",
                        'foreignField': "_id",
                        'as': "home"
                    }
                },
                {'$unwind': '$home'}]

    # cursor de habitaciones con su hogar
    cursor = db_room.aggregate(pipeline)

    # convertir los datos anteriores, de bson a json
    response = json_util.dumps(cursor)

    # se devuelve la respuesta en formato json
    return Response(response, mimetype='application/json')


# Método para obtener las habitaciones
def get_all_rooms():
    # obtener datos de mongodb (formato bson originalmente)
    rooms = db_room.find()
    
    # convertir los datos anteriores, de bson a json
    response = json_util.dumps(rooms)

    # se devuelve la respuesta en formato json
    return Response(response, mimetype='application/json')


# Método para obtener una habitación
def get_one_room(id):
    # se comprueba si el id introducido es válido
    is_valid_id = bson.ObjectId.is_valid(id)

    # si el id introducido no es válido se muestra mensaje de error
    if not is_valid_id:
        response = jsonify({'response': 'ERROR. the entered id is not valid.'})
        return response
        
    # obtener datos de mongodb (formato bson originalmente)
    room = db_room.find_one({'_id': ObjectId(id)})

    if room == None:
        response = jsonify({'response': 'ERROR. the entered id does not exist.'})
        return response
    
    # convertir los datos anteriores, de bson a json
    response = json_util.dumps(room)
    
    # se devuelve la respuesta en formato json
    return Response(response, mimetype='application/json')


# Método para obtener una habitación filtrando por descripción
def get_rooms_by_description():
    # obtener datos de la petición (datos json)
    data = request.json

    # comprobar si se han introducido datos (body json)
    if data == None:
        response = jsonify({'response': 'ERROR. no value has been entered.'})
        return response

    # validar si el contenido json es válido
    is_valid, msg = validate_json('schemas/schema_search_by_desc.json', data)

    # si el contenido json no es válido, se muestra respuesta
    if is_valid == False:
        response = jsonify({
            'response': 'ERROR. The value entered is not valid',
            'message': msg})
        return response

    # filtro para buscar coincidencias en el campo 'description'
    filter = {'description': {'$regex': request.json['description']}}

    # se realiza la búsqueda con el filtro anterior
    query = db_room.find(filter=filter)

    # convertir los datos anteriores, de bson a json
    response = json_util.dumps(query)

    # se devuelve la respuesta en formato json
    return Response(response, mimetype='application/json')


# Método para eliminar una habitación
def delete_room(id):
    # se comprueba si el id introducido es válido
    is_valid_id = bson.ObjectId.is_valid(id)

    # si el id introducido no es válido se muestra mensaje de error
    if not is_valid_id:
        response = jsonify({'response': 'ERROR. the entered id is not valid.'})
        return response
        
    # obtener datos de mongodb (formato bson originalmente)
    room = db_room.find_one({'_id': ObjectId(id)})

    if room == None:
        response = jsonify({'response': 'ERROR. the entered id does not exist.'})
        return response

    db_room.delete_one({'_id': ObjectId(id)})
    response = jsonify({'response': 'Room (' + id + ') was deleted successfully'})
    return response


# Método para actualizar un hogar
def update_room(id):
    """ se comprueba el id de la habitación introducido por parámetro """
    # se comprueba si el id introducido es válido
    is_valid_id = bson.ObjectId.is_valid(id)

    # si el id introducido no es válido se muestra mensaje de error
    if not is_valid_id:
        response = jsonify({'response': 'ERROR. the entered id is not valid.'})
        return response
        
    # obtener datos de mongodb (formato bson originalmente)
    room = db_room.find_one({'_id': ObjectId(id)})

    if room == None:
        response = jsonify({'response': 'ERROR. the entered id does not exist.'})
        return response

    """ actualizar la habitación existente """
    # obtener datos de la petición (datos json)
    data = request.json

    # validar si el contenido json es válido
    is_valid, msg = validate_json('schemas/schema_room.json', data)

    # si el contenido json no es válido, se muestra respuesta
    if is_valid == False:
        response = jsonify({
            'response': 'ERROR. The value entered is not valid',
            'message': msg})
        return response

    # comprobar si la habitación introducida existe. (se busca por el campo description)
    room_exists = db_room.find_one({'description': request.json['description']})

    # Si la habitación existe (obtenida en la búsqueda)...
    if room_exists != None:
        response = jsonify({'response': 'ERROR. The room introduced already exists'})

    # db_room.update_one({'_id': ObjectId(id)}, {'$set': data})
    db_room.update_one({'_id': ObjectId(id)}, {
                       '$set': {'description': data['description'], 'floor': data['floor']}})

    response = jsonify(
        {
            'response': 'Room (' + id + ') was updated successfully',
            'message': msg
        })
        
    return response