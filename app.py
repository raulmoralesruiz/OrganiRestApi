# Importar librerías 
from flask import Flask, jsonify, request, Response
from flask.wrappers import Request
from flask_pymongo import PyMongo
# from werkzeug.security import generate_password_hash, check_password_hash
from bson import json_util
from bson.objectid import ObjectId
from flask_cors import CORS

import json
import jsonschema
from jsonschema import validate

# Ejecutar aplicación Flask
app = Flask(__name__)
app.config['MONGO_URI']='mongodb://test:test@127.0.0.1:27017/organi?authSource=admin'
mongo = PyMongo(app)

# Variable para definir un acceso directo al documento de usuarios
db_home = mongo.db.home

# Deshabilitar errores de CORS en navegadores
CORS(app)


# Ruta para crear un hogar
@app.route('/home', methods=['POST'])

# Método para crear un hogar
def create_home():
    # obtener datos de la petición (datos json)
    data = request.json

    # validar si el contenido json es válido
    is_valid, msg = validate_home_json(data)

    # comprobar si el hogar introducido existe. (se busca por el campo description)
    home_exists = db_home.find_one({'description': request.json['description']})

    # Si el hogar existe (se ha obtenido algún hogar en la búsqueda)...
    if home_exists != None:
        response = jsonify({'response': 'ERROR. The home introduced already exists'})
    # Si el hogar no existe...
    else:        
        if is_valid:
            # insertar hogar y almacenar id
            home_id = str(db_home.insert_one(data).inserted_id)

            response = jsonify(
                {
                    'response': 'Home (' + home_id + ') was created successfully',
                    'message': msg
                })
        else:
            response = jsonify(
                {
                    'response': 'ERROR. The value entered is not valid',
                    'message': msg
                })
    return response


def get_home_schema():
    """This function loads the given schema available"""
    with open('schema_home.json', 'r') as file:
        schema = json.load(file)
    return schema

def validate_home_json(json_data):
    """REF: https://json-schema.org/ """
    # Describe what kind of json you expect.
    execute_api_schema = get_home_schema()

    try:
        validate(instance=json_data, schema=execute_api_schema)
    except jsonschema.exceptions.ValidationError as err:
        print(err)
        err = "Given JSON data is InValid"
        return False, err

    message = "Given JSON data is Valid"
    return True, message


# Ruta para obtener los hogares
@app.route('/home', methods=['GET'])

# Método para obtener los hogares
def get_homes():
    # obtener datos de mongodb (formato bson originalmente)
    homes = db_home.find()
    # convertir los datos anteriores, de bson a json
    response = json_util.dumps(homes)
    # enviar datos convertidos al cliente
    return Response(response, mimetype='application/json')


# Ruta para obtener un hogar
@app.route('/home/<id>', methods=['GET'])

# Método para obtener un hogar
def get_home(id):
    # obtener datos de mongodb (formato bson originalmente)
    home = db_home.find_one({'_id': ObjectId(id)})
    # convertir los datos anteriores, de bson a json
    response = json_util.dumps(home)
    # enviar datos convertidos al cliente
    return Response(response, mimetype='application/json')


# Ruta para eliminar un hogar
@app.route('/home/<id>', methods=['DELETE'])

# Método para eliminar un hogar
def delete_home(id):
    db_home.delete_one({'_id': ObjectId(id)})
    response = jsonify({'response': 'Home (' + id + ') was deleted successfully'})
    return response


# Ruta para actualizar un hogar
@app.route('/home/<id>', methods=['PUT'])

# Método para actualizar un hogar
def update_user(id):
    # obtener datos de la petición
    data = request.json
    is_valid, msg = validate_home_json(data)

    if is_valid:
        db_home.update_one({'_id': ObjectId(id)}, {'$set': data})

        response = jsonify(
            {
                'response': 'Home (' + id + ') was updated successfully',
                'message': msg
            })
    else:
        response = jsonify(
            {
                'response': 'ERROR. The value entered is not valid',
                'message': msg
            })
    return response


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