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
app.config['MONGO_URI']='mongodb://kirkdax:b*jEeJfM7T*y!X@192.168.1.30:27017/organi?authSource=admin'
mongo = PyMongo(app)

# Deshabilitar errores de CORS en navegadores
CORS(app)


""" -------------------- HOME - START -------------------- """
# Ruta para obtener todos los contenedores
@app.route('/homes', methods=['GET'])

# Método para obtener todos los contenedores
def home_get_all_homes():
    return get_all_homes()
""" -------------------- HOME - END -------------------- """


""" -------------------- ROOM - START -------------------- """
# Ruta para obtener todas las habitaciones
@app.route('/rooms', methods=['POST'])

# Método para obtener todas las habitaciones
def room_get_all_rooms():
    return get_all_rooms()
""" -------------------- ROOM - END -------------------- """


""" -------------------- CONTAINER - START -------------------- """
# Ruta para obtener todas las habitaciones
@app.route('/containers', methods=['POST'])

# Método para obtener todas las habitaciones
def container_get_all_containers():
    return get_all_containers()
""" -------------------- CONTAINER - END -------------------- """


""" -------------------- COMPARTMENT - START -------------------- """
# Ruta para obtener todas las habitaciones
@app.route('/compartments', methods=['POST'])

# Método para obtener todas las habitaciones
def compartment_get_all_compartments():
    return get_all_compartments()
""" -------------------- COMPARTMENT - END -------------------- """


""" -------------------- ITEM - START -------------------- """
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


# Ruta para crear un artículo
@app.route('/item/search', methods=['POST'])

# Método para crear un artículo
def item_search_item():
    return search_item()
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