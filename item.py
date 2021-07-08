from flask import jsonify, request, Response

import bson
from bson import json_util
from bson.objectid import ObjectId
from pymongo import MongoClient
from datetime import datetime


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

# Variable para definir un acceso directo al documento de artículoss
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
    item_exists = db_item.find_one({'description': request.json['description']})

    # Si el artículo existe (se ha obtenido artículo en la búsqueda)...
    if item_exists != None:
        response = jsonify({'response': 'ERROR. The entered item already exists'})
        return response

    # agregar relación id_compartment en artículo
    data["id_compartment"] = ObjectId(id_compartment)

    # Si el artículo no existe, se inserta el artículo y se almacena id
    item_id = str(db_item.insert_one(data).inserted_id)

    response = jsonify(
        {
            'response': 'item was created successfully',
            # 'message': msg,
            'new_item': item_id
        })
    return response
    

# Método para obtener los artículos con su compartimento correspondiente
def get_item_with_compartment():
    # parámetros para aggregate
    pipeline = [{'$lookup':
                    {
                        'from': "compartment",
                        'localField': "id_compartment",
                        'foreignField': "_id",
                        'as': "compartment"
                    }
                },
                {'$unwind': '$compartment'}]

    # cursor de artículos con su compartimento
    cursor = db_item.aggregate(pipeline)

    # convertir los datos anteriores, de bson a json
    response = json_util.dumps(cursor)

    # se devuelve la respuesta en formato json
    return Response(response, mimetype='application/json')


# Método para obtener los artículos
def get_all_items():
    # obtener datos de mongodb (formato bson originalmente)
    items = db_item.find()
    
    # convertir los datos anteriores, de bson a json
    response = json_util.dumps(items)

    # se devuelve la respuesta en formato json
    return Response(response, mimetype='application/json')


# Método para obtener un artículo
def get_one_item(id):
    # se comprueba si el id introducido es válido
    is_valid_id = bson.ObjectId.is_valid(id)

    # si el id introducido no es válido se muestra mensaje de error
    if not is_valid_id:
        response = jsonify({'response': 'ERROR. the entered id is not valid.'})
        return response
        
    # obtener datos de mongodb (formato bson originalmente)
    item = db_item.find_one({'_id': ObjectId(id)})

    if item == None:
        response = jsonify({'response': 'ERROR. the entered id does not exist.'})
        return response
    
    # convertir los datos anteriores, de bson a json
    response = json_util.dumps(item)
    # se devuelve la respuesta en formato json
    return Response(response, mimetype='application/json')


# Método para obtener artículos filtrando por descripción
def get_items_by_description():
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
    query = db_item.find(filter=filter)

    # convertir los datos anteriores, de bson a json
    response = json_util.dumps(query)

    # se devuelve la respuesta en formato json
    return Response(response, mimetype='application/json')


# Método para eliminar un compartimento
def delete_item(id):
    # se comprueba si el id introducido es válido
    is_valid_id = bson.ObjectId.is_valid(id)

    # si el id introducido no es válido se muestra mensaje de error
    if not is_valid_id:
        response = jsonify({'response': 'ERROR. the entered id is not valid.'})
        return response
        
    # obtener datos de mongodb (formato bson originalmente)
    item = db_item.find_one({'_id': ObjectId(id)})

    if item == None:
        response = jsonify({'response': 'ERROR. the entered id does not exist.'})
        return response

    db_item.delete_one({'_id': ObjectId(id)})
    response = jsonify({'response': 'Container (' + id + ') was deleted successfully'})
    return response


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
    item = db_item.find_one({'_id': ObjectId(id_item)})
    package = db_item.find_one({'_id': ObjectId(id_package)})

    if item == None:
        response = jsonify({'response': 'ERROR. the entered id_item does not exist.'})
        return response
    if package == None:
        response = jsonify({'response': 'ERROR. the entered id_package does not exist.'})
        return response        

    """ actualizar el artículo existente """
    # se crea embalaje (diccionario) para el artículo
    data = { 'package': ObjectId(id_package) }
    
    db_item.update_one({'_id': ObjectId(id_item)}, {'$set': data})

    response = jsonify(
        {
            'response': 'Container (' + id_item + ') was updated successfully',
            # 'message': msg,
            'new_package': id_package
        })
        
    return response



# Método para actualizar un artículo
def update_item(id):
    """ se comprueba el id introducido por parámetro """
    # se comprueba si el id introducido es válido
    is_valid_id = bson.ObjectId.is_valid(id)

    # si el id introducido no es válido se muestra mensaje de error
    if not is_valid_id:
        response = jsonify({'response': 'ERROR. the entered id is not valid.'})
        return response
        
    # obtener datos de mongodb (formato bson originalmente)
    item = db_item.find_one({'_id': ObjectId(id)})

    if item == None:
        response = jsonify({'response': 'ERROR. the entered id does not exist.'})
        return response

    """ actualizar contenedor existente """
    # obtener datos de la petición (datos json)
    data = request.json

    # date_request_json = db_item.find_one({
    #     'description': request.json['description'],
    #     'purchase_date': request.json['purchase_date']})
        
    # print('date_request_json')
    # print(date_request_json)

    # if date_request_json != None:
    #     # expresión regular para la fecha
    #     regex_date = "%Y-%m-%d" # "%Y-%m-%d %H:%M:%S"

    #     # control del campo purchase_date
    #     try:
    #         date_in_datetime = datetime.strptime(request.json['purchase_date'], regex_date)
    #     except:
    #         response = jsonify({'response': 'ERROR. The entered purchase_date is not valid'})
    #         return response

    #     # modificar el campo purchase_date para insertarlo como datetime
    #     data["purchase_date"] = date_in_datetime

    # validar si el contenido json es válido
    is_valid, msg = validate_json('schemas/schema_item.json', data)

    # si el contenido json no es válido, se muestra respuesta
    if is_valid == False:
        response = jsonify({
            'response': 'ERROR. The value entered is not valid',
            'message': msg})
        return response

    # comprobar si existe. (se busca por el campo description)
    item_exists = db_item.find_one({'description': request.json['description']})

    # Si existe (obtenida en la búsqueda)...
    if item_exists != None:
        response = jsonify({'response': 'ERROR. The item introduced already exists'})

    db_item.update_one({'_id': ObjectId(id)}, {
                       '$set': {
                           'description': request.json['description'],
                           'color': request.json['color'],
                           'brand': request.json['brand'],
                           'model': request.json['model'],
                           'group': request.json['group'],
                           'price': request.json['price'],
                           'store_link': request.json['store_link'],
                           'serial_number': request.json['serial_number'],
                        #    'purchase_date': request.json['purchase_date'],
                           'warranty_years': request.json['color'],
                           }})

    response = jsonify(
        {
            'response': 'Container (' + id + ') was updated successfully',
            'message': msg
        })
        
    return response


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
