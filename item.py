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

# Variable para definir un acceso directo al documento de compartimentos
db_item = db.item


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

    # validar si el contenido json es válido
    is_valid, msg = validate_json('schemas/schema_item.json', data)

    # si el contenido json no es válido, se muestra respuesta
    if is_valid == False:
        response = jsonify({
            'response': 'ERROR. The value entered is not valid',
            'message': msg})
        return response

    # comprobar si el compartimento introducido existe. (se busca por el campo description)
    item_exists = db_item.find_one({'description': request.json['description']})

    # Si el compartimento existe (se ha obtenido compartimento en la búsqueda)...
    if item_exists != None:
        response = jsonify({'response': 'ERROR. The entered item already exists'})
        return response

    # agregar relación id_compartment en compartimento
    data["id_compartment"] = ObjectId(id_compartment)

    # Si el compartimento no existe, se inserta el compartimento y se almacena id
    item_id = str(db_item.insert_one(data).inserted_id)

    response = jsonify(
        {
            'response': 'item was created successfully',
            # 'message': msg,
            'new_item': item_id
        })
    return response
    

# # Método para obtener los compartimentos con su contenedor correspondiente
# def get_compartment_with_container():
#     # parámetros para aggregate
#     pipeline = [{'$lookup':
#                     {
#                         'from': "container",
#                         'localField': "id_container",
#                         'foreignField': "_id",
#                         'as': "container"
#                     }
#                 },
#                 {'$unwind': '$container'}]

#     # cursor de compartimentos con su contenedor
#     cursor = db_compartment.aggregate(pipeline)

#     # convertir los datos anteriores, de bson a json
#     response = json_util.dumps(cursor)

#     # se devuelve la respuesta en formato json
#     return Response(response, mimetype='application/json')


# # Método para obtener los compartimentos
# def get_all_compartments():
#     # obtener datos de mongodb (formato bson originalmente)
#     compartments = db_compartment.find()
    
#     # convertir los datos anteriores, de bson a json
#     response = json_util.dumps(compartments)

#     # se devuelve la respuesta en formato json
#     return Response(response, mimetype='application/json')


# # Método para obtener un compartimento
# def get_one_compartment(id):
#     # se comprueba si el id introducido es válido
#     is_valid_id = bson.ObjectId.is_valid(id)

#     # si el id introducido no es válido se muestra mensaje de error
#     if not is_valid_id:
#         response = jsonify({'response': 'ERROR. the entered id is not valid.'})
#         return response
        
#     # obtener datos de mongodb (formato bson originalmente)
#     compartment = db_compartment.find_one({'_id': ObjectId(id)})

#     if compartment == None:
#         response = jsonify({'response': 'ERROR. the entered id does not exist.'})
#         return response
    
#     # convertir los datos anteriores, de bson a json
#     response = json_util.dumps(compartment)
#     # se devuelve la respuesta en formato json
#     return Response(response, mimetype='application/json')


# # Método para eliminar un compartimento
# def delete_compartment(id):
#     # se comprueba si el id introducido es válido
#     is_valid_id = bson.ObjectId.is_valid(id)

#     # si el id introducido no es válido se muestra mensaje de error
#     if not is_valid_id:
#         response = jsonify({'response': 'ERROR. the entered id is not valid.'})
#         return response
        
#     # obtener datos de mongodb (formato bson originalmente)
#     compartment = db_compartment.find_one({'_id': ObjectId(id)})

#     if compartment == None:
#         response = jsonify({'response': 'ERROR. the entered id does not exist.'})
#         return response

#     db_compartment.delete_one({'_id': ObjectId(id)})
#     response = jsonify({'response': 'Container (' + id + ') was deleted successfully'})
#     return response


# # Método para actualizar un compartimento
# def update_compartment(id):
#     """ se comprueba el id introducido por parámetro """
#     # se comprueba si el id introducido es válido
#     is_valid_id = bson.ObjectId.is_valid(id)

#     # si el id introducido no es válido se muestra mensaje de error
#     if not is_valid_id:
#         response = jsonify({'response': 'ERROR. the entered id is not valid.'})
#         return response
        
#     # obtener datos de mongodb (formato bson originalmente)
#     compartment = db_compartment.find_one({'_id': ObjectId(id)})

#     if compartment == None:
#         response = jsonify({'response': 'ERROR. the entered id does not exist.'})
#         return response

#     """ actualizar contenedor existente """
#     # obtener datos de la petición (datos json)
#     data = request.json

#     # validar si el contenido json es válido
#     is_valid, msg = validate_json('schemas/schema_compartment.json', data)

#     # si el contenido json no es válido, se muestra respuesta
#     if is_valid == False:
#         response = jsonify({
#             'response': 'ERROR. The value entered is not valid',
#             'message': msg})
#         return response

#     # comprobar si la habitación introducida existe. (se busca por el campo description)
#     compartment_exists = db_compartment.find_one({'row': request.json['row'], 'column': request.json['column']})

#     # Si la habitación existe (obtenida en la búsqueda)...
#     if compartment_exists != None:
#         response = jsonify({'response': 'ERROR. The compartment introduced already exists'})

#     db_compartment.update_one({'_id': ObjectId(id)}, {
#                        '$set': {'row': request.json['row'], 'column': request.json['column']}})

#     response = jsonify(
#         {
#             'response': 'Container (' + id + ') was updated successfully',
#             'message': msg
#         })
        
#     return response


""" Métodos auxiliares/comunes """

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