from flask import jsonify, request, Response

import bson
from bson import json_util
from bson.objectid import ObjectId
from jsonschema.exceptions import ValidationError
from pymongo import MongoClient

import json
import jsonschema
from jsonschema import validate

from keys import mongo_uri


# Método que genera la conexión con el servidor mongo
def link_server():
    return MongoClient(mongo_uri)


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
        err = "Given JSON data is not valid"
        # err = ValidationError(err.message)
        return False, err

    message = "Given JSON data is valid"
    return True, message


# Método que comprueba la petición (datos json) mediante jsonschema
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


''' ---------- CRUD ---------- '''
# Método para obtener todos los documentos
def get_all_documents(id_user, col):
    # obtener datos de mongodb (formato bson originalmente)
    documents = col.find({'user_id':id_user})

    # convertir los datos anteriores, de bson a json
    response = json_util.dumps(documents)

    # se devuelve la respuesta en formato json
    return Response(response, mimetype='application/json')


# Método para obtener un documento
def get_one_document(id_user, id_doc, col):
    # se comprueba si el documento existe y es válido
    res, doc = check_document(id_user, id_doc, col)
    if res != 'ok':
        return jsonify(res)

    # convertir los datos anteriores, de bson a json
    response = json_util.dumps(doc)

    # se devuelve la respuesta en formato json
    return Response(response, mimetype='application/json')


# Método para obtener un documento filtrando por descripción
def get_documents_by_description(id_user, col):
    # se validan los datos de la petición (json)
    data, res = validate_request_json('schemas/schema_search_by_desc.json')
    if res != "ok":
        return jsonify(res)

    # filtro para buscar coincidencias en el campo 'description'
    filter = {'user_id': id_user, 'description': {
              '$regex': request.json['description'], '$options': 'i'}}

    # se realiza la búsqueda con el filtro anterior
    query = col.find(filter=filter)

    # convertir los datos anteriores, de bson a json
    response = json_util.dumps(query)

    # se devuelve la respuesta en formato json
    return Response(response, mimetype='application/json')


# Método para obtener las documentos padre e hijo (Ejemplo: Hogar y habitación)
def get_father_with_son(col, father):
    # parámetros para aggregate
    pipeline = [{'$lookup': {
        'from': str(father),
        'localField': "id_" + str(father),
        'foreignField': "_id",
        'as': str(father)
    }
    }, {'$unwind': '$' + str(father)}]

    # cursor de habitaciones con su hogar
    cursor = col.aggregate(pipeline)

    # convertir los datos anteriores, de bson a json
    response = json_util.dumps(cursor)

    # se devuelve la respuesta en formato json
    return Response(response, mimetype='application/json')


# Método para eliminar un documento
def delete_document(id_user, id_doc, col, doc_type, col_archive):
    # se comprueba si el documento existe y es válido
    res, doc = check_document(id_user, id_doc, col)
    if res != 'ok':
        return jsonify(res)

    # se archiva el documento antes de borrarlo
    doc = col.find_one({'_id': ObjectId(id_doc)})
    col_archive.insert_one(doc)

    # se borra el documento
    col.delete_one({'_id': ObjectId(id_doc)})

    response = jsonify({
        'response': doc_type + ' was deleted successfully',
        doc_type: id_doc
        })

    return response


# Método para actualizar un documento
def update_document(id, col, doc_type, doc_schema_update):
    # se comprueba si el documento existe y es válido
    res, doc = check_document(id, col)
    if res != 'ok':
        return jsonify(res)

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
            # se obtiene id del objeto
            item_id_in_data = str(doc_exists['_id'])

            # se comprueba si coindice id pasado por parametro e id pasado por body
            if item_id_in_data != id:
                response = jsonify({'response': 'ERROR. The entered ' + doc_type + ' already exists'})
                return response

    col.update_one({'_id': ObjectId(id)}, {'$set': data})

    response = jsonify({
        'response': doc_type + ' was updated successfully',
        doc_type: id
    })

    return response


# Método para crear un documento
def create_document(id_father, col_father, doc_type_father, son_schema, col_son, doc_type_son):
    # se comprueba si el documento padre existe y es válido
    res, doc = check_document(id_father, col_father)
    if res != 'ok':
        return jsonify(res)

    # insertar documento
    return insert_document(son_schema, col_son, doc_type_son, id_father, doc_type_father)


# Método auxiliar de create_document. Comprueba un documento padre
def check_document(id_user, id_doc, col_doc):
    # se comprueba si el id introducido es válido
    is_valid_id = bson.ObjectId.is_valid(id_doc)

    # respuesta por defecto
    response = "ok"
    doc = None

    # si el id introducido no es válido se muestra mensaje de error
    if not is_valid_id:
        response = {
            'response': 'The entered id_document is not valid.',
            'status': 'ERROR',
        }
        return response, doc

    # obtener diccionario de mongodb (formato bson originalmente)
    doc = col_doc.find_one({'user_id':id_user, '_id': ObjectId(id_doc)})

    # comprobar si el id pasado por parámetro coincide con algún documento de la base de datos
    if doc == None:
        response = {
            'response': 'The entered id_document does not exist.',
            'status': 'ERROR',
        }

    return response, doc


# Método auxiliar de create_document. Inserta un documento
def insert_document(doc_schema, col, doc_type, id_father, doc_type_father):
    # se validan los datos de la petición (json)
    data, res = validate_request_json(doc_schema)
    if res != "ok":
        return jsonify(res)

    # comprobar si el documento hijo introducido existe. (se busca por el campo description)
    if doc_type == 'compartment':
        # son_exists = col.find_one({'row': request.json['row'], 'column': request.json['column']})
        son_exists = col.find_one({'row': request.json['row'], 'column': request.json['column'], "id_container": ObjectId(id_father)})
    else:
        son_exists = col.find_one({'description': request.json['description']})

    if son_exists != None:
        response = jsonify({
            'response': 'The entered ' + doc_type + ' already exists',
            'status': 'ERROR',
        })
        return response

    if id_father != None:
        # agregar relación id_father en el documento hijo
        data["id_" + str(doc_type_father)] = ObjectId(id_father)

    # Si el documento hijo no existe, se inserta y se almacena id
    doc_id = str(col.insert_one(data).inserted_id)

    response = jsonify({
        'response': doc_type + ' was created successfully',
        'new_' + doc_type : doc_id
    })
    return response


def get_section(col, section, query):
    # se define cursor con todos los hogares
    cursor = col.distinct(section, query)

    # convertir los datos anteriores, de bson a json
    response = json_util.dumps(cursor)

    # se devuelve la respuesta en formato json
    return Response(response, mimetype='application/json')
