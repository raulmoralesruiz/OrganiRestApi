from flask import jsonify, request
from common_methods import *

# Conexión al servidor MongoDB
client = link_server()

# Conexión a la base de datos
db = client["organi"]

# Colección home
col = db.home


# Método para crear un hogar
def create_home():
    # se validan los datos de la petición (json)
    data, res = validate_request_json('schemas/schema_home.json')
    if res != "ok":
        return jsonify(res)

    # comprobar si el hogar introducido existe. (buscando por 'description')
    home_exists = col.find_one({'description': request.json['description']})
    if home_exists != None:
        response = jsonify({'response': 'ERROR. The entered home already exists'})
        return response
        
    # Si no existe, se inserta y se almacena id
    home_id = str(col.insert_one(data).inserted_id)

    response = jsonify({
        'response': 'Home was created successfully',
        'new_home': home_id
    })
    return response


# Método para obtener los hogares
def get_homes():
    return get_all_documents(col)


# Método para obtener un hogar
def get_home_by_id(id):
    return get_one_document(id, col)


# Método para obtener un hogar filtrando por descripción
def get_homes_by_description():
    return get_documents_by_description(col)


# Método para eliminar un hogar
def delete_home(id):
    doc_type = 'home'
    return delete_document(id, col, doc_type)


# Método para actualizar un hogar
def update_home(id):
    doc_type = 'home'
    doc_schema_update = 'schemas/home/schema_home_update.json'
    return update_document(id, col, doc_type, doc_schema_update)