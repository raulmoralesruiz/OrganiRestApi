# Importar librerías 
from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
from flask_cors import CORS

from home import *

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
def home_get_homes():
    return get_homes()


# Ruta para obtener un hogar
@app.route('/home/<id>', methods=['GET'])

# Método para obtener un hogar
def home_get_home(id):
    return get_home(id)


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