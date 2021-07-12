from flask import jsonify

import bson
from bson.objectid import ObjectId

from common_methods import *


# Conexión al servidor MongoDB
client = link_server()

# Conexión a la base de datos
db = client["organi"]

# Colección compartment
col = db.compartment

# Variable que indica el nombre/tipo del documento actual
doc_type = 'compartment'


# Método para crear un compartimento
def create_compartment_manual(id_container):
    col_father = db.container
    doc_type_father = 'container'
    son_schema = 'schemas/compartment/schema_compartment.json'
    doc_type_son = doc_type
    return create_document(id_container, col_father, doc_type_father, son_schema, col, doc_type_son)
    

# Método para crear un compartimento
def create_compartment_auto(id_container, number_of_rows, number_of_columns):
    number_of_rows = int(number_of_rows)
    number_of_columns = int(number_of_columns)

    col_father = db.container

    # se comprueba si el documento padre existe y es válido
    res, doc = check_document(id_container, col_father)
    if res != 'ok':
        return jsonify(res)

    # insertar compartimentos
    for column in range(number_of_columns):
        for row in range(number_of_rows):
            # comprobar si el compartimento introducido existe.
            compartment_exists = col.find_one({
                # 'name': "C" + str(column + 1) + "-R" + str(row + 1),
                'row': "R" + str(row + 1),
                'column': "C" + str(column + 1),
                "id_container": ObjectId(id_container)})

            # Si el compartimento existe se muestra mensaje de error
            if compartment_exists != None:
                response = jsonify({
                    'response': 'The entered ' + doc_type + ' already exists',
                    'status': 'ERROR'
                })
                return response

            # Se crea cada compartimento
            new_compartment = {
                "row": "R" + str(row + 1),
                "column": "C" + str(column + 1),
                # "name": "C" + str(column + 1) + "-R" + str(row + 1),
                "id_container": ObjectId(id_container)
            }

            # Si el compartimento no existe se inserta
            col.insert_one(new_compartment)

    response = jsonify({
        'response': doc_type + ' was created successfully',
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
