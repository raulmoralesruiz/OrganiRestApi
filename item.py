from flask import jsonify, request, Response

import bson
from bson import json_util
from bson.objectid import ObjectId
from pymongo import MongoClient
from datetime import datetime

import json
import jsonschema
from jsonschema import validate

from common_methods import *


# Conexión al servidor MongoDB
client = link_server()

# Conexión a la base de datos
db = client["organi"]

# Variable para definir un acceso directo al documento de artículoss
col = db.item


# Método para crear un artículo
def create_item(id_compartment):
    """ comprobar id_compartment """
    # se comprueba si el id introducido es válido
    is_valid_id = bson.ObjectId.is_valid(id_compartment)

    # si el id introducido no es válido se muestra mensaje de error
    if not is_valid_id:
        response = jsonify({'response': 'ERROR. The entered id is not valid.'})
        return response

    # obtener diccionario 'compartment' de mongodb (formato bson originalmente)
    compartment = db.compartment.find_one({'_id': ObjectId(id_compartment)})
    
    # comprobar si el id pasado por parámetro coincide con algún hogar de la base de datos
    if compartment == None:
        response = jsonify({'response': 'ERROR. The entered id does not exist.'})
        return response

    """ insertar artículo """
    # obtener datos de la petición (datos json)
    data = request.json

    # expresión regular para fechas
    regex_date = "%Y-%m-%d"
    full_regex_date = "%Y-%m-%d %H:%M:%S"

    # control del campo purchase_date
    try:
        date_in_datetime = datetime.strptime(request.json['purchase_date'], regex_date)
    except:
        response = jsonify({'response': 'ERROR. The entered purchase_date is not valid'})
        return response

    # modificar el campo purchase_date para insertarlo como datetime
    data["purchase_date"] = date_in_datetime

    # añadir campo con la fecha de creación
    data['creation_date'] = datetime.strptime(datetime.now().strftime(full_regex_date), full_regex_date)

    # validar si el contenido json es válido
    is_valid, msg = validate_json('schemas/schema_item.json', data)

    # si el contenido json no es válido, se muestra respuesta
    if is_valid == False:
        response = jsonify({
            'response': 'ERROR. The value entered is not valid',
            'message': msg})
        return response

    # comprobar si el artículo introducido existe. (se busca por el campo description)
    item_exists = col.find_one({'description': request.json['description']})

    # Si el artículo existe (se ha obtenido artículo en la búsqueda)...
    if item_exists != None:
        response = jsonify({'response': 'ERROR. The entered item already exists'})
        return response

    # agregar relación id_compartment en artículo
    data["id_compartment"] = ObjectId(id_compartment)

    # Si el artículo no existe, se inserta el artículo y se almacena id
    item_id = str(col.insert_one(data).inserted_id)

    response = jsonify(
        {
            'response': 'item was created successfully',
            # 'message': msg,
            'new_item': item_id
        })
    return response
    

# Método para obtener los artículos con su compartimento correspondiente
def get_item_with_compartment():
    father = 'compartment'
    return get_father_with_son(col, father)


# Método para obtener los artículos
def get_all_items():
    return get_all_documents(col)


# Método para obtener un artículo
def get_one_item(id):
    return get_one_document(id, col)


# Método para obtener artículos filtrando por descripción
def get_items_by_description():
    return get_documents_by_description(col)


# Método para eliminar un compartimento
def delete_item(id):
    doc_type = 'item'
    return delete_document(id, col, doc_type)


# Método para actualizar un artículo
def update_item(id):
    doc_type = 'item'
    doc_schema_update = 'schemas/item/schema_item_update.json'
    return update_document(id, col, doc_type, doc_schema_update)


# Método para añadir el embalaje (item) a un artículo (otro item)
def add_package_to_item(id_item, id_package):
    """ se comprueba el id de el artículo introducido por parámetro """
    # se comprueba si el id introducido es válido
    is_valid_id_item = bson.ObjectId.is_valid(id_item)
    is_valid_id_package = bson.ObjectId.is_valid(id_package)

    # si el id introducido no es válido se muestra mensaje de error
    if not is_valid_id_item:
        response = jsonify({'response': 'ERROR. the entered id_item is not valid.'})
        return response
    if not is_valid_id_package:
        response = jsonify({'response': 'ERROR. the entered id_package is not valid.'})
        return response

    # se comprueba si ambos id son iguales
    if id_item == id_package:
        response = jsonify({'response': 'ERROR. id_package and id_item are equal.'})
        return response
        
    # obtener datos de mongodb (formato bson originalmente)
    item = col.find_one({'_id': ObjectId(id_item)})
    package = col.find_one({'_id': ObjectId(id_package)})

    if item == None:
        response = jsonify({'response': 'ERROR. the entered id_item does not exist.'})
        return response
    if package == None:
        response = jsonify({'response': 'ERROR. the entered id_package does not exist.'})
        return response        

    """ actualizar el artículo existente """
    # se crea embalaje (diccionario) para el artículo
    data = { 'package': ObjectId(id_package) }

    col.update_one({'_id': ObjectId(id_item)}, {'$set': data})

    response = jsonify({
        'response': 'container was updated successfully',
        'new_package': id_package,
        'item': id_item
    })
        
    return response
