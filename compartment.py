from flask import jsonify, request

import bson
from bson.objectid import ObjectId

from common_methods import *


# Conexión al servidor MongoDB
client = link_server()

# Conexión a la base de datos
db = client["organi"]

# Variable para definir un acceso directo al documento de compartimentos
col = db.compartment


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
    compartment_exists = col.find_one({'row': request.json['row'], 'column': request.json['column']})

    # Si el compartimento existe (se ha obtenido compartimento en la búsqueda)...
    if compartment_exists != None:
        response = jsonify({'response': 'ERROR. The entered compartment already exists'})
        return response

    # agregar relación id_container en compartimento
    data["id_container"] = ObjectId(id_container)

    # Si el compartimento no existe, se inserta el compartimento y se almacena id
    compartment_id = str(col.insert_one(data).inserted_id)

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
            compartment_exists = col.find_one(
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
            col.insert_one(new_compartment)

    response = jsonify(
        {
            'response': 'compartment was created successfully',
            'number_of_columns': number_of_columns,
            'number_of_rows': number_of_rows,
        })
    return response


# Método para obtener los compartimentos con su contenedor correspondiente
def get_compartment_with_container():
    father = 'container'
    return get_father_with_son(col, father)


# Método para obtener los compartimentos
def get_all_compartments():
    return get_all_documents(col)


# Método para obtener un compartimento
def get_one_compartment(id):
    return get_one_document(id, col)


# Método para eliminar un compartimento
def delete_compartment(id):
    doc_type = 'compartment'
    return delete_document(id, col, doc_type)


# Método para actualizar un compartimento
def update_compartment(id):
    doc_type = 'compartment'
    doc_schema_update = 'schemas/compartment/schema_compartment_update.json'
    return update_document(id, col, doc_type, doc_schema_update)