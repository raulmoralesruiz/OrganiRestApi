from flask import jsonify, request

import bson
from bson.objectid import ObjectId

from common_methods import *


# Conexión al servidor MongoDB
client = link_server()

# Conexión a la base de datos
db = client["organi"]

# Variable para definir un acceso directo al documento de hogares (home)
col = db.room


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
    room_exists = col.find_one({'description': request.json['description']})

    # Si la habitación existe (se ha obtenido alguna habitación en la búsqueda)...
    if room_exists != None:
        response = jsonify({'response': 'ERROR. The entered room already exists'})
        return response

    # agregar relación id_home en habitación
    data["id_home"] = ObjectId(id_home)

    # Si la habitación no existe, se inserta la habitación y se almacena id
    room_id = str(col.insert_one(data).inserted_id)

    response = jsonify(
        {
            'response': 'Room was created successfully',
            'new_room': room_id
        })
    return response
    

# Método para obtener las habitaciones con su hogar correspondiente
def get_room_with_home():
    father = 'home'
    return get_father_with_son(col, father)


# Método para obtener todas las habitaciones
def get_all_rooms():
    return get_all_documents(col)


# Método para obtener una habitación
def get_one_room(id):
    return get_one_document(id, col)


# Método para obtener una habitación filtrando por descripción
def get_rooms_by_description():
    return get_documents_by_description(col)


# Método para eliminar una habitación
def delete_room(id):
    doc_type = 'room'
    return delete_document(id, col, doc_type)


# Método para actualizar un hogar
def update_room(id):
    doc_type = 'room'
    doc_schema_update = 'schemas/room/schema_room_update.json'
    return update_document(id, col, doc_type, doc_schema_update)