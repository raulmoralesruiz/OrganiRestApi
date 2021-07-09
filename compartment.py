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

# Variable para definir un acceso directo al documento de compartimentos
db_compartment = db.compartment


# Método para crear un compartimento
def create_compartment_manual(id_container):
    """ comprobar id_container """
    # se comprueba si el id introducido es válido
    is_valid_id = bson.ObjectId.is_valid(id_container)

    # si el id introducido no es válido se muestra mensaje de error
    if not is_valid_id:
        response = jsonify({'response': 'ERROR. The entered id is not valid.'})
        return response

    # obtener diccionario 'container' de mongodb (formato bson originalmente)
    container = db.container.find_one({'_id': ObjectId(id_container)})
    
    # comprobar si el id pasado por parámetro coincide con algún hogar de la base de datos
    if container == None:
        response = jsonify({'response': 'ERROR. The entered id does not exist.'})
        return response

    """ insertar compartimento """
    # obtener datos de la petición (datos json)
    data = request.json

    # validar si el contenido json es válido
    is_valid, msg = validate_json('schemas/schema_compartment.json', data)

    # si el contenido json no es válido, se muestra respuesta
    if is_valid == False:
        response = jsonify({
            'response': 'ERROR. The value entered is not valid',
            'message': msg})
        return response

    # comprobar si el compartimento introducido existe. (se busca por el campo description)
    compartment_exists = db_compartment.find_one({'row': request.json['row'], 'column': request.json['column']})

    # Si el compartimento existe (se ha obtenido compartimento en la búsqueda)...
    if compartment_exists != None:
        response = jsonify({'response': 'ERROR. The entered compartment already exists'})
        return response

    # agregar relación id_container en compartimento
    data["id_container"] = ObjectId(id_container)

    # Si el compartimento no existe, se inserta el compartimento y se almacena id
    compartment_id = str(db_compartment.insert_one(data).inserted_id)

    response = jsonify(
        {
            'response': 'compartment was created successfully',
            # 'message': msg,
            'new_compartment': compartment_id
        })
    return response
    

# Método para crear un compartimento
def create_compartment_auto(id_container, number_of_rows, number_of_columns):
    number_of_rows = int(number_of_rows)
    number_of_columns = int(number_of_columns)

    """ comprobar id_container """
    # se comprueba si el id introducido es válido
    is_valid_id = bson.ObjectId.is_valid(id_container)

    # si el id introducido no es válido se muestra mensaje de error
    if not is_valid_id:
        response = jsonify({'response': 'ERROR. The entered id is not valid.'})
        return response

    # obtener diccionario 'container' de mongodb (formato bson originalmente)
    container = db.container.find_one({'_id': ObjectId(id_container)})
    
    # comprobar si el id pasado por parámetro coincide con algún hogar de la base de datos
    if container == None:
        response = jsonify({'response': 'ERROR. The entered id does not exist.'})
        return response

    """ insertar compartimentos """
    for col in range(number_of_columns):
        for row in range(number_of_rows):
            # comprobar si el compartimento introducido existe.
            compartment_exists = db_compartment.find_one(
                {'name': "C" + str(col + 1) + "-R" + str(row + 1), "id_container": ObjectId(id_container)})

            # Si el compartimento existe se muestra mensaje de error
            if compartment_exists != None:
                response = jsonify({'response': 'ERROR. The entered compartment already exists'})
                return response

            # Se crea cada compartimento
            new_compartment = {
                "row": "C" + str(col + 1),
                "column": "R" + str(row + 1),
                "name": "C" + str(col + 1) + "-R" + str(row + 1),
                "id_container": ObjectId(id_container)
            }

            # Si el compartimento no existe se inserta
            db_compartment.insert_one(new_compartment)

    response = jsonify(
        {
            'response': 'compartment was created successfully',
            'number_of_columns': number_of_columns,
            'number_of_rows': number_of_rows,
        })
    return response


# Método para obtener los compartimentos con su contenedor correspondiente
def get_compartment_with_container():
    # parámetros para aggregate
    pipeline = [{'$lookup':
                    {
                        'from': "container",
                        'localField': "id_container",
                        'foreignField': "_id",
                        'as': "container"
                    }
                },
                {'$unwind': '$container'}]

    # cursor de compartimentos con su contenedor
    cursor = db_compartment.aggregate(pipeline)

    # convertir los datos anteriores, de bson a json
    response = json_util.dumps(cursor)

    # se devuelve la respuesta en formato json
    return Response(response, mimetype='application/json')


# Método para obtener los compartimentos
def get_all_compartments():
    # obtener datos de mongodb (formato bson originalmente)
    compartments = db_compartment.find()
    
    # convertir los datos anteriores, de bson a json
    response = json_util.dumps(compartments)

    # se devuelve la respuesta en formato json
    return Response(response, mimetype='application/json')


# Método para obtener un compartimento
def get_one_compartment(id):
    # se comprueba si el id introducido es válido
    is_valid_id = bson.ObjectId.is_valid(id)

    # si el id introducido no es válido se muestra mensaje de error
    if not is_valid_id:
        response = jsonify({'response': 'ERROR. the entered id is not valid.'})
        return response
        
    # obtener datos de mongodb (formato bson originalmente)
    compartment = db_compartment.find_one({'_id': ObjectId(id)})

    if compartment == None:
        response = jsonify({'response': 'ERROR. the entered id does not exist.'})
        return response
    
    # convertir los datos anteriores, de bson a json
    response = json_util.dumps(compartment)
    # se devuelve la respuesta en formato json
    return Response(response, mimetype='application/json')


# Método para eliminar un compartimento
def delete_compartment(id):
    # se comprueba si el id introducido es válido
    is_valid_id = bson.ObjectId.is_valid(id)

    # si el id introducido no es válido se muestra mensaje de error
    if not is_valid_id:
        response = jsonify({'response': 'ERROR. the entered id is not valid.'})
        return response
        
    # obtener datos de mongodb (formato bson originalmente)
    compartment = db_compartment.find_one({'_id': ObjectId(id)})

    if compartment == None:
        response = jsonify({'response': 'ERROR. the entered id does not exist.'})
        return response

    db_compartment.delete_one({'_id': ObjectId(id)})
    response = jsonify({'response': 'Container (' + id + ') was deleted successfully'})
    return response


# Método para actualizar un compartimento
def update_compartment(id):
    """ se comprueba el id introducido por parámetro """
    # se comprueba si el id introducido es válido
    is_valid_id = bson.ObjectId.is_valid(id)

    # si el id introducido no es válido se muestra mensaje de error
    if not is_valid_id:
        response = jsonify({'response': 'ERROR. the entered id is not valid.'})
        return response
        
    # obtener datos de mongodb (formato bson originalmente)
    compartment = db_compartment.find_one({'_id': ObjectId(id)})

    if compartment == None:
        response = jsonify({'response': 'ERROR. the entered id does not exist.'})
        return response

    """ actualizar contenedor existente """
    # obtener datos de la petición (datos json)
    data = request.json

    # validar si el contenido json es válido
    is_valid, msg = validate_json('schemas/schema_compartment.json', data)

    # si el contenido json no es válido, se muestra respuesta
    if is_valid == False:
        response = jsonify({
            'response': 'ERROR. The value entered is not valid',
            'message': msg})
        return response

    # comprobar si la habitación introducida existe. (se busca por el campo description)
    compartment_exists = db_compartment.find_one({'row': request.json['row'], 'column': request.json['column']})

    # Si la habitación existe (obtenida en la búsqueda)...
    if compartment_exists != None:
        response = jsonify({'response': 'ERROR. The compartment introduced already exists'})

    db_compartment.update_one({'_id': ObjectId(id)}, {
                       '$set': {'row': request.json['row'], 'column': request.json['column']}})

    response = jsonify(
        {
            'response': 'Container (' + id + ') was updated successfully',
            'message': msg
        })
        
    return response