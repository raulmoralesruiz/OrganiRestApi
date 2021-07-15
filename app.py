# Importar librerías 
from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
from flask_cors import CORS

from home import *
from room import *
from container import *
from compartment import *
# from item import *
from item_new import *


# Ejecutar aplicación Flask
app = Flask(__name__)
app.config['MONGO_URI']='mongodb://kirkdax:b*jEeJfM7T*y!X@192.168.1.220:27017/organi?authSource=admin'
mongo = PyMongo(app)

# Deshabilitar errores de CORS en navegadores
CORS(app)


""" -------------------- HOME - START -------------------- """
# Ruta para obtener todos los contenedores
@app.route('/homes/description', methods=['GET'])

# Método para obtener todos los contenedores
def home_get_home_descriptions():
    return get_home_descriptions()


# Ruta para obtener todos los contenedores
@app.route('/homes/address', methods=['GET'])

# Método para obtener todos los contenedores
def home_get_home_addresses():
    return get_home_addresses()
""" -------------------- HOME - END -------------------- """


""" -------------------- ROOM - START -------------------- """
# Ruta para obtener todas las habitaciones
@app.route('/rooms', methods=['GET'])

# Método para obtener todas las habitaciones
def room_get_all_rooms():
    return get_all_rooms()
""" -------------------- ROOM - END -------------------- """


""" -------------------- CONTAINER - START -------------------- """
# Ruta para obtener todos los contenedores
@app.route('/containers/description', methods=['GET'])

# Método para obtener todos los contenedores
def container_get_container_descriptions():
    return get_container_descriptions()


# Ruta para obtener todos los contenedores
@app.route('/containers/color', methods=['GET'])

# Método para obtener todos los contenedores
def container_get_container_colors():
    return get_container_colors()
""" -------------------- CONTAINER - END -------------------- """


""" -------------------- COMPARTMENT - START -------------------- """
# Ruta para crear un compartimento manualmente
@app.route('/compartment/<id_container>', methods=['POST'])

# Método para crear un compartimento manualmente
def compartment_create_manual(id_container):
    return create_compartment_manual(id_container)


# Ruta para obtener todos los contenedores
@app.route('/compartments', methods=['GET'])

# Método para obtener todos los contenedores
def container_get_all_compartments():
    return get_all_compartments()


# Ruta para obtener un contenedor, filtrando por id
@app.route('/compartment/<id_compartment>', methods=['GET'])

# Método para obtener un contenedor, filtrando por id
def compartment_get_one_compartment(id_compartment):
    return get_one_compartment(id_compartment)


# Ruta para crear un compartimento automáticamente
@app.route('/compartment/<id_container>/<number_of_rows>/<number_of_columns>', methods=['POST'])

# Método para crear un compartimento automáticamente
def compartment_create_auto(id_container, number_of_rows, number_of_columns):
    return create_compartment_auto(id_container, number_of_rows, number_of_columns)


# Ruta para obtener los compartimentos con su contenedor correspondiente
@app.route('/compartment/container', methods=['GET'])

# Método para obtener los compartimentos con su contenedor correspondiente
def compartment_get_compartments_with_container():
    return get_compartment_with_container()


# Ruta para eliminar un compartimento, filtrando por id
@app.route('/compartment/<id>', methods=['DELETE'])

# Método para eliminar un compartimento, filtrando por id
def compartment_delete_compartment(id):
    return delete_compartment(id)


# Ruta para actualizar una habitación
@app.route('/compartment/<id>', methods=['PUT'])

# Método para actualizar una habitación
def compartment_update_compartment(id):
    return update_compartment(id)
""" -------------------- COMPARTMENT - END -------------------- """


""" -------------------- ITEM - START -------------------- """
# # Ruta para crear un artículo
# @app.route('/item/<id_compartment>', methods=['POST'])

# # Método para crear un artículo
# def item_create_manual(id_compartment):
#     return create_item(id_compartment)


# Ruta para crear un artículo
@app.route('/item', methods=['POST'])

# Método para crear un artículo
def item_create_item():
    return create_item()


# Ruta para obtener todos los artículos
@app.route('/items', methods=['GET'])

# Método para obtener todos los artículos
def item_get_all_items():
    return get_all_items()


# Ruta para obtener un contenedor, filtrando por id
@app.route('/item/<id_item>', methods=['GET'])

# Método para obtener un contenedor, filtrando por id
def item_get_one_item(id_item):
    return get_one_item(id_item)


# # Ruta para obtener los artículos con su compartimento correspondiente
# @app.route('/item/compartment', methods=['GET'])

# # Método para obtener los artículos con su compartimento correspondiente
# def item_get_items_with_compartment():
#     return get_item_with_compartment()


# Ruta para obtener los artículos, filtrando por descripción
@app.route('/item/description', methods=['POST'])

# Método para obtener los artículos, filtrando por descripción
def item_get_items_by_description():
    return get_items_by_description()


# Ruta para eliminar un artículo, filtrando por id
@app.route('/item/<id>', methods=['DELETE'])

# Método para eliminar un artículo, filtrando por id
def item_delete_item(id):
    return delete_item(id)


# Ruta para actualizar un artículo
@app.route('/item/<id>', methods=['PUT'])

# Método para actualizar un artículo
def item_update_item(id):
    return update_item(id)


# Ruta para actualizar un artículo
@app.route('/item/<id_item>/<id_package>', methods=['PUT'])

# Método para actualizar un artículo
def item_add_package_to_item(id_item, id_package):
    return add_package_to_item(id_item, id_package)
""" -------------------- ITEM - END -------------------- """


# Ruta para controlar errores
@app.errorhandler(404)

# Método para controlar errores
def not_found(error = None):
    response = jsonify({
        'response': 'Resource not found ' + request.url,
        'status': 404,
    })
    response.status_code = 404
    return response 


if __name__ == '__main__':
    app.run(debug=True, port=4000)



# """ -------------------- HOME - START -------------------- """
# # Ruta para crear un hogar
# @app.route('/home', methods=['POST'])

# # Método para crear un hogar
# def home_create():
#     return create_home()


# # Ruta para obtener los hogares
# @app.route('/home', methods=['GET'])

# # Método para obtener los hogares
# def home_get_all_homes():
#     return get_homes()


# # Ruta para obtener los hogares, filtrando por descripción
# @app.route('/home/description', methods=['GET'])

# # Método para obtener los hogares, filtrando por descripción
# def home_get_homes_by_description():
#     return get_homes_by_description()


# # Ruta para obtener un hogar , filtrando por _id
# @app.route('/home/<id>', methods=['GET'])

# # Método para obtener un hogar , filtrando por _id
# def home_get_home_by_id(id):
#     return get_home_by_id(id)


# # Ruta para eliminar un hogar
# @app.route('/home/<id>', methods=['DELETE'])

# # Método para eliminar un hogar
# def home_delete_home(id):
#     return delete_home(id)


# # Ruta para actualizar un hogar
# @app.route('/home/<id>', methods=['PUT'])

# # Método para actualizar un hogar
# def home_update_home(id):
#     return update_home(id)
# """ -------------------- HOME - END -------------------- """


# """ -------------------- ROOM - START -------------------- """
# # Ruta para crear una habitación
# @app.route('/room/<id_home>', methods=['POST'])

# # Método para crear una habitación
# def room_create(id_home):
#     return create_room(id_home)

# # Ruta para obtener todas las habitaciones
# @app.route('/rooms', methods=['GET'])

# # Método para obtener todas las habitaciones
# def room_get_all_rooms():
#     return get_all_rooms()


# # Ruta para obtener una habitación, filtrando por id
# @app.route('/room/<id_room>', methods=['GET'])

# # Método para obtener una habitación, filtrando por id
# def room_get_one_room(id_room):
#     return get_one_room(id_room)


# # Ruta para obtener las habitaciones con su hogar correspondiente
# @app.route('/rooms/home', methods=['GET'])

# # Método para obtener las habitaciones con su hogar correspondiente
# def room_get_rooms_with_home():
#     return get_room_with_home()


# # Ruta para obtener las habitaciones, filtrando por descripción
# @app.route('/room/description', methods=['GET'])

# # Método para obtener las habitaciones, filtrando por descripción
# def room_get_rooms_by_description():
#     return get_rooms_by_description()


# # Ruta para eliminar una habitación, filtrando por id
# @app.route('/room/<id>', methods=['DELETE'])

# # Método para eliminar una habitación, filtrando por id
# def room_delete_room(id):
#     return delete_room(id)


# # Ruta para actualizar una habitación
# @app.route('/room/<id>', methods=['PUT'])

# # Método para actualizar una habitación
# def room_update_room(id):
#     return update_room(id)
# """ -------------------- ROOM - END -------------------- """


# """ -------------------- CONTAINER - START -------------------- """
# # Ruta para crear un contenedor
# @app.route('/container/<id_room>', methods=['POST'])

# # Método para crear un contenedor
# def container_create(id_room):
#     return create_container(id_room)


# # Ruta para obtener todos los contenedores
# @app.route('/containers', methods=['GET'])

# # Método para obtener todos los contenedores
# def container_get_all_containers():
#     return get_all_containers()


# # Ruta para obtener un contenedor, filtrando por id
# @app.route('/container/<id_container>', methods=['GET'])

# # Método para obtener un contenedor, filtrando por id
# def container_get_one_container(id_container):
#     return get_one_container(id_container)


# # Ruta para obtener los contenedores con su habitación correspondiente
# @app.route('/container/room', methods=['GET'])

# # Método para obtener los contenedores con su habitación correspondiente
# def container_get_containers_with_room():
#     return get_container_with_room()


# # Ruta para obtener los contenedores, filtrando por descripción
# @app.route('/container/description', methods=['GET'])

# # Método para obtener los contenedores, filtrando por descripción
# def container_get_containers_by_description():
#     return get_containers_by_description()


# # Ruta para eliminar un contenedor, filtrando por id
# @app.route('/container/<id>', methods=['DELETE'])

# # Método para eliminar un contenedor, filtrando por id
# def container_delete_container(id):
#     return delete_container(id)


# # Ruta para actualizar una habitación
# @app.route('/container/<id>', methods=['PUT'])

# # Método para actualizar una habitación
# def container_update_container(id):
#     return update_container(id)
# """ -------------------- CONTAINER - END -------------------- """


# """ -------------------- COMPARTMENT - START -------------------- """
# # Ruta para crear un compartimento manualmente
# @app.route('/compartment/<id_container>', methods=['POST'])

# # Método para crear un compartimento manualmente
# def compartment_create_manual(id_container):
#     return create_compartment_manual(id_container)


# # Ruta para obtener todos los contenedores
# @app.route('/compartments', methods=['GET'])

# # Método para obtener todos los contenedores
# def container_get_all_compartments():
#     return get_all_compartments()


# # Ruta para obtener un contenedor, filtrando por id
# @app.route('/compartment/<id_compartment>', methods=['GET'])

# # Método para obtener un contenedor, filtrando por id
# def compartment_get_one_compartment(id_compartment):
#     return get_one_compartment(id_compartment)


# # Ruta para crear un compartimento automáticamente
# @app.route('/compartment/<id_container>/<number_of_rows>/<number_of_columns>', methods=['POST'])

# # Método para crear un compartimento automáticamente
# def compartment_create_auto(id_container, number_of_rows, number_of_columns):
#     return create_compartment_auto(id_container, number_of_rows, number_of_columns)


# # Ruta para obtener los compartimentos con su contenedor correspondiente
# @app.route('/compartment/container', methods=['GET'])

# # Método para obtener los compartimentos con su contenedor correspondiente
# def compartment_get_compartments_with_container():
#     return get_compartment_with_container()


# # Ruta para eliminar un compartimento, filtrando por id
# @app.route('/compartment/<id>', methods=['DELETE'])

# # Método para eliminar un compartimento, filtrando por id
# def compartment_delete_compartment(id):
#     return delete_compartment(id)


# # Ruta para actualizar una habitación
# @app.route('/compartment/<id>', methods=['PUT'])

# # Método para actualizar una habitación
# def compartment_update_compartment(id):
#     return update_compartment(id)
# """ -------------------- COMPARTMENT - END -------------------- """