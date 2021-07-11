from flask import jsonify, request

import bson
from bson.objectid import ObjectId

from common_methods import *


# Conexión al servidor MongoDB
client = link_server()

# Conexión a la base de datos
db = client["organi"]

# Variable para definir un acceso directo al documento de contenedores
col = db.container


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
    container_exists = col.find_one({'description': request.json['description']})

    # Si el contenedor existe (se ha obtenido contenedor en la búsqueda)...
    if container_exists != None:
        response = jsonify({'response': 'ERROR. The entered container already exists'})
        return response

    # agregar relación id_room en contenedor
    data["id_room"] = ObjectId(id_room)

    # Si el contenedor no existe, se inserta el contenedor y se almacena id
    container_id = str(col.insert_one(data).inserted_id)

    response = jsonify(
        {
            'response': 'container was created successfully',
            # 'message': msg,
            'new_container': container_id
        })
    return response
    

# Método para obtener los contenedores con su habitación correspondiente
def get_container_with_room():
    father = 'room'
    return get_father_with_son(col, father)


# Método para obtener los contenedores
def get_all_containers():
    return get_all_documents(col)


# Método para obtener un contenedor
def get_one_container(id):
    return get_one_document(id, col)


# Método para obtener un contenedor filtrando por descripción
def get_containers_by_description():
    return get_documents_by_description(col)


# Método para eliminar un contenedor
def delete_container(id):
    doc_type = 'container'
    return delete_document(id, col, doc_type)


# Método para actualizar un contenedor
def update_container(id):
    doc_type = 'container'
    doc_schema_update = 'schemas/container/schema_container_update.json'
    return update_document(id, col, doc_type, doc_schema_update)