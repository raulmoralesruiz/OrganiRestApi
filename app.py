# Importar librerías 
from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
from flask_cors import CORS

from home import *
from room import *

# Ejecutar aplicación Flask
app = Flask(__name__)
app.config['MONGO_URI']='mongodb://test:test@127.0.0.1:27017/organi?authSource=admin'
mongo = PyMongo(app)

# Deshabilitar errores de CORS en navegadores
CORS(app)


""" -------------------- HOME - START -------------------- """
# Ruta para crear un hogar
@app.route('/home', methods=['POST'])

# Método para crear un hogar
def home_create():
    return create_home()


# Ruta para obtener los hogares
@app.route('/home', methods=['GET'])

# Método para obtener los hogares
def home_get_all_homes():
    return get_homes()


# Ruta para obtener los hogares, filtrando por descripción
@app.route('/home/description', methods=['GET'])

# Método para obtener los hogares, filtrando por descripción
def home_get_homes_by_description():
    return get_homes_by_description()


# Ruta para obtener un hogar , filtrando por _id
@app.route('/home/<id>', methods=['GET'])

# Método para obtener un hogar , filtrando por _id
def home_get_home_by_id(id):
    return get_home_by_id(id)


# Ruta para eliminar un hogar
@app.route('/home/<id>', methods=['DELETE'])

# Método para eliminar un hogar
def home_delete_home(id):
    return delete_home(id)


# Ruta para actualizar un hogar
@app.route('/home/<id>', methods=['PUT'])

# Método para actualizar un hogar
def home_update_home(id):
    return update_home(id)
""" -------------------- HOME - END -------------------- """


""" -------------------- ROOM - START -------------------- """
# Ruta para crear una habitación
@app.route('/room/<id_home>', methods=['POST'])

# Método para crear una habitación
def room_create(id_home):
    return create_room(id_home)

# Ruta para obtener todas las habitaciones
@app.route('/room/<id_home>', methods=['GET'])

# Método para obtener todas las habitaciones
def room_get_all_rooms(id_home):
    return get_rooms(id_home)
""" -------------------- ROOM - END -------------------- """


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