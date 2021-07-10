from flask import jsonify, request, Response

import bson
from bson import json_util
from bson.objectid import ObjectId
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
        err = "Given JSON data is not valid"
        return False, err

    message = "Given JSON data is valid"
    return True, message


# obtener datos de la petición (datos json)
def validate_request_json(url_jsonschema):
    data = request.json

    # validar si el contenido json es válido
    is_valid, msg = validate_json(url_jsonschema, data)

    # respuesta por defecto
    response = "ok"

    # si el contenido json no es válido, se muestra respuesta
    if is_valid == False:
        response = {
            'status': 'ERROR',
            'response': msg}

    return data, response



''' CRUD '''
# Método para obtener todos los documentos
def get_all_documents(col):
    # obtener datos de mongodb (formato bson originalmente)
    documents = col.find()
    
    # convertir los datos anteriores, de bson a json
    response = json_util.dumps(documents)

    # se devuelve la respuesta en formato json
    return Response(response, mimetype='application/json')


# Método para obtener un documento
def get_one_document(id, col):
    # se comprueba si el id introducido es válido
    is_valid_id = bson.ObjectId.is_valid(id)

    # si el id introducido no es válido se muestra mensaje de error
    if not is_valid_id:
        response = jsonify({'response': 'ERROR. the entered id is not valid.'})
        return response
        
    # obtener datos de mongodb (formato bson originalmente)
    doc = col.find_one({'_id': ObjectId(id)})

    if doc == None:
        response = jsonify({'response': 'ERROR. the entered id does not exist.'})
        return response
    
    # convertir los datos anteriores, de bson a json
    response = json_util.dumps(doc)
    
    # se devuelve la respuesta en formato json
    return Response(response, mimetype='application/json')


# Método para obtener un documento filtrando por descripción
def get_documents_by_description(col):
    # obtener datos de la petición (datos json)
    data = request.json

    # comprobar si se han introducido datos (body json)
    if data == None:
        response = jsonify({'response': 'ERROR. No value has been entered.'})
        return response

    # validar si el contenido json es válido
    is_valid, msg = validate_json('schemas/schema_search_by_desc.json', data)

    # si el contenido json no es válido, se muestra respuesta
    if is_valid == False:
        response = jsonify({
            'response': 'ERROR. The entered value is not valid',
            'message': msg})
        return response

    # filtro para buscar coincidencias en el campo 'description'
    filter = {'description': {'$regex': request.json['description']}}

    # se realiza la búsqueda con el filtro anterior
    query = col.find(filter=filter)

    # convertir los datos anteriores, de bson a json
    response = json_util.dumps(query)

    # se devuelve la respuesta en formato json
    return Response(response, mimetype='application/json')


# Método para obtener las documentos padre e hijo (Ejemplo: Hogar y habitación)
def get_father_with_son(col, father):
    # parámetros para aggregate
    pipeline = [{'$lookup':
                    {
                        'from': str(father),
                        'localField': "id_" + str(father),
                        'foreignField': "_id",
                        'as': str(father)
                    }
                },
                {'$unwind': '$' + str(father)}]

    # cursor de habitaciones con su hogar
    cursor = col.aggregate(pipeline)

    # convertir los datos anteriores, de bson a json
    response = json_util.dumps(cursor)

    # se devuelve la respuesta en formato json
    return Response(response, mimetype='application/json')


# Método para eliminar un documento
def delete_document(id, col, doc_type):
    # se comprueba si el id introducido es válido
    is_valid_id = bson.ObjectId.is_valid(id)

    # si el id introducido no es válido se muestra mensaje de error
    if not is_valid_id:
        response = jsonify({'response': 'ERROR. the entered id is not valid.'})
        return response
        
    # obtener datos de mongodb (formato bson originalmente)
    room = col.find_one({'_id': ObjectId(id)})

    if room == None:
        response = jsonify({'response': 'ERROR. the entered id does not exist.'})
        return response

    col.delete_one({'_id': ObjectId(id)})
    
    response = jsonify({
        'response': doc_type + ' was deleted successfully',
        doc_type: id
        })
    
    return response


# Método para actualizar un documento
def update_document(id, col, doc_type, doc_schema_update):
    # se comprueba el id introducido por parámetro
    is_valid_id = bson.ObjectId.is_valid(id)

    # si el id introducido no es válido se muestra mensaje de error
    if not is_valid_id:
        response = jsonify({'response': 'ERROR. the entered id is not valid.'})
        return response
        
    # obtener datos de mongodb (formato bson originalmente)
    item = col.find_one({'_id': ObjectId(id)})

    if item == None:
        response = jsonify({'response': 'ERROR. the entered id does not exist.'})
        return response

    """ actualizar documento """
    # se validan los datos de la petición (json)
    data, res = validate_request_json(doc_schema_update)
    if res != "ok":
        return jsonify(res)

    # Se comprueba si en la petición existe 'description'
    if 'description' in data:
        # comprobar si existe.
        doc_exists = col.find_one({'description': request.json['description']})

        # Si existe (se ha obtenido resultado en la búsqueda)...
        if doc_exists != None:
            response = jsonify({'response': 'ERROR. The entered home already exists'})
            return response

    col.update_one({'_id': ObjectId(id)}, {'$set': data})

    response = jsonify({
        'response': doc_type + ' was updated successfully',
        doc_type: id
    })
        
    return response