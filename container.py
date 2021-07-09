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

# Variable para definir un acceso directo al documento de contenedores
db_container = db.container


# Método para crear un contenedor
def create_container(id_room):
    """ comprobar id_room """
    # se comprueba si el id introducido es válido
    is_valid_id = bson.ObjectId.is_valid(id_room)

    # si el id introducido no es válido se muestra mensaje de error
    if not is_valid_id:
        response = jsonify({'response': 'ERROR. The entered id is not valid.'})
        return response

    # obtener diccionario 'room' de mongodb (formato bson originalmente)
    room = db.room.find_one({'_id': ObjectId(id_room)})
    
    # comprobar si el id pasado por parámetro coincide con algún hogar de la base de datos
    if room == None:
        response = jsonify({'response': 'ERROR. The entered id does not exist.'})
        return response

    """ insertar contenedor """
    # obtener datos de la petición (datos json)
    data = request.json

    # validar si el contenido json es válido
    is_valid, msg = validate_json('schemas/schema_container.json', data)

    # si el contenido json no es válido, se muestra respuesta
    if is_valid == False:
        response = jsonify({
            'response': 'ERROR. The value entered is not valid',
            'message': msg})
        return response

    # comprobar si el contenedor introducido existe. (se busca por el campo description)
    container_exists = db_container.find_one({'description': request.json['description']})

    # Si el contenedor existe (se ha obtenido contenedor en la búsqueda)...
    if container_exists != None:
        response = jsonify({'response': 'ERROR. The entered container already exists'})
        return response

    # agregar relación id_room en contenedor
    data["id_room"] = ObjectId(id_room)

    # Si el contenedor no existe, se inserta el contenedor y se almacena id
    container_id = str(db_container.insert_one(data).inserted_id)

    response = jsonify(
        {
            'response': 'container was created successfully',
            # 'message': msg,
            'new_container': container_id
        })
    return response
    

# Método para obtener los contenedores con su habitación correspondiente
def get_container_with_room():
    # parámetros para aggregate
    pipeline = [{'$lookup':
                    {
                        'from': "room",
                        'localField': "id_room",
                        'foreignField': "_id",
                        'as': "room"
                    }
                },
                {'$unwind': '$room'}]

    # cursor de contenedores con su habitación
    cursor = db_container.aggregate(pipeline)

    # convertir los datos anteriores, de bson a json
    response = json_util.dumps(cursor)

    # se devuelve la respuesta en formato json
    return Response(response, mimetype='application/json')


# Método para obtener los contenedores
def get_all_containers():
    # obtener datos de mongodb (formato bson originalmente)
    containers = db_container.find()
    
    # convertir los datos anteriores, de bson a json
    response = json_util.dumps(containers)

    # se devuelve la respuesta en formato json
    return Response(response, mimetype='application/json')


# Método para obtener un contenedor
def get_one_container(id):
    # se comprueba si el id introducido es válido
    is_valid_id = bson.ObjectId.is_valid(id)

    # si el id introducido no es válido se muestra mensaje de error
    if not is_valid_id:
        response = jsonify({'response': 'ERROR. the entered id is not valid.'})
        return response
        
    # obtener datos de mongodb (formato bson originalmente)
    container = db_container.find_one({'_id': ObjectId(id)})

    if container == None:
        response = jsonify({'response': 'ERROR. the entered id does not exist.'})
        return response
    
    # convertir los datos anteriores, de bson a json
    response = json_util.dumps(container)
    # se devuelve la respuesta en formato json
    return Response(response, mimetype='application/json')


# Método para obtener un contenedor filtrando por descripción
def get_containers_by_description():
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
    query = db_container.find(filter=filter)

    # convertir los datos anteriores, de bson a json
    response = json_util.dumps(query)

    # se devuelve la respuesta en formato json
    return Response(response, mimetype='application/json')


# Método para eliminar un contenedor
def delete_container(id):
    # se comprueba si el id introducido es válido
    is_valid_id = bson.ObjectId.is_valid(id)

    # si el id introducido no es válido se muestra mensaje de error
    if not is_valid_id:
        response = jsonify({'response': 'ERROR. the entered id is not valid.'})
        return response
        
    # obtener datos de mongodb (formato bson originalmente)
    container = db_container.find_one({'_id': ObjectId(id)})

    if container == None:
        response = jsonify({'response': 'ERROR. the entered id does not exist.'})
        return response

    db_container.delete_one({'_id': ObjectId(id)})
    response = jsonify({'response': 'Container (' + id + ') was deleted successfully'})
    return response


# Método para actualizar un contenedor
def update_container(id):
    """ se comprueba el id de la habitación introducido por parámetro """
    # se comprueba si el id introducido es válido
    is_valid_id = bson.ObjectId.is_valid(id)

    # si el id introducido no es válido se muestra mensaje de error
    if not is_valid_id:
        response = jsonify({'response': 'ERROR. the entered id is not valid.'})
        return response
        
    # obtener datos de mongodb (formato bson originalmente)
    container = db_container.find_one({'_id': ObjectId(id)})

    if container == None:
        response = jsonify({'response': 'ERROR. the entered id does not exist.'})
        return response

    """ actualizar la habitación existente """
    # obtener datos de la petición (datos json)
    data = request.json

    # validar si el contenido json es válido
    is_valid, msg = validate_json('schemas/schema_container.json', data)

    # si el contenido json no es válido, se muestra respuesta
    if is_valid == False:
        response = jsonify({
            'response': 'ERROR. The value entered is not valid',
            'message': msg})
        return response

    # comprobar si la habitación introducida existe. (se busca por el campo description)
    container_exists = db_container.find_one({'description': request.json['description']})

    # Si la habitación existe (obtenida en la búsqueda)...
    if container_exists != None:
        response = jsonify({'response': 'ERROR. The container introduced already exists'})

    # db_container.update_one({'_id': ObjectId(id)}, {'$set': data})
    db_container.update_one({'_id': ObjectId(id)}, {
                       '$set': {'description': data['description'], 'color': data['color']}})

    response = jsonify(
        {
            'response': 'Container (' + id + ') was updated successfully',
            'message': msg
        })
        
    return response