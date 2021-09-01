# Importar librerías
from flask import Flask, jsonify, request, session, flash
from flask_pymongo import PyMongo
from flask_cors import CORS
from functools import wraps
import jwt
from datetime import datetime, timedelta
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
import re

from home import *
from room import *
from container import *
from compartment import *
from item_new import *
from keys import *


# Ejecutar aplicación Flask
app = Flask(__name__)
app.config['MONGO_URI'] = mongo_uri
app.config['SECRET_KEY'] = secret_key
mongo = PyMongo(app)

# Deshabilitar errores de CORS en navegadores
CORS(app)


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return 'Unauthorized Access!', 401

        try:
            col_user = mongo.db.user
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = col_user.find_one({'user_id': data['user_id']})
            if not current_user:
                return 'Unauthorized Access!', 401
        except:
            return 'Unauthorized Access!', 401
        return f(*args, **kwargs)

    return decorated


@app.route('/login', methods=['POST'])
def login():
    response = {
        "success" : False,
        "message" : "Invalid parameters",
        "token" : ""
    }
    try:
        col_user = mongo.db.user
        auth = request.json

        if not auth or not auth.get('email') or not auth.get('password'):
            response["message"] = 'Invalid data'
            return response, 422

        user = col_user.find_one({'email': auth['email']})

        if not user:
            response["message"] = "Unauthorized Access!"
            return response, 401

        if check_password_hash(user['password'], auth['password']):
            token = jwt.encode({
                'user_id': user['user_id'],
                'exp': datetime.utcnow() + timedelta(hours=24)
            }, app.config['SECRET_KEY'])
            response["message"] = "token generated"
            response["token"] = token.decode('UTF-8')
            response["success"] = True
            return response, 200
        response["message"] = 'Invalid email or password'
        return response, 403
    except Exception as ex:
        print(str(ex))
        return response, 422


@app.route('/signup', methods=['POST'])
# @token_required
def signup():
    response = {
        "success": False,
        "message": "Invalid parameters"
    }
    try:
        col_user = mongo.db.user
        data = request.json
        name, email = data.get('name'), data.get('email')
        password = data.get('password')
        if name == None or email == None or password == None:
            return response, 202
        if check_email(email) == False:
            response["message"] = "Invalid email address"
            return response, 202
        if check_password(password) == False:
            response["message"] = "Password requirement not fullfilled"
            return response, 202
        user = col_user.find_one({'email': (email.lower()).strip()})
        if not user:
            col_user.insert_one({'user_id': str(uuid.uuid4()), 'user_name': name,
                                 'email': email, 'password': generate_password_hash(password)})
            response["success"] = True
            response["message"] = 'Successfully registered'
            return response, 200
        else:
            response["message"] = 'User already exists. Please Log in'
            return response, 202
    except Exception as ex:
        print(str(ex))
        return response, 422


## Utils
def check_email(email):
    if(re.search("([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)", email.lower())):
        return True
    else:
        return False


def check_password(password):
    if len(password) >= 8 and len(password) <= 20 and any(char.isdigit() for char in password) \
        and any(char.isupper() for char in password) and any(char.islower() for char in password):
        return True
    else:
        return False


""" -------------------- HOME - START -------------------- """
# Ruta para obtener los hogares
@app.route('/homes/<id_user>', methods=['GET'])
@token_required
def home_get_all_homes(id_user):
    return get_all_homes(id_user)
""" -------------------- HOME - END -------------------- """


""" -------------------- ROOM - START -------------------- """
# Ruta para obtener las habitaciones
@app.route('/rooms/<id_user>', methods=['POST'])
@token_required
def room_get_all_rooms(id_user):
    return get_all_rooms(id_user)
""" -------------------- ROOM - END -------------------- """


""" -------------------- CONTAINER - START -------------------- """
# Ruta para obtener los contenedores
@app.route('/containers/<id_user>', methods=['POST'])
@token_required
def container_get_all_containers(id_user):
    return get_all_containers(id_user)
""" -------------------- CONTAINER - END -------------------- """


""" -------------------- COMPARTMENT - START -------------------- """
# Ruta para obtener los compartimentos
@app.route('/compartments/<id_user>', methods=['POST'])
@token_required
def compartment_get_all_compartments(id_user):
    return get_all_compartments(id_user)
""" -------------------- COMPARTMENT - END -------------------- """


""" -------------------- ITEM - START -------------------- """
# crear un artículo
@app.route('/item/<id_user>', methods=['POST'])
@token_required
def item_create_item(id_user):
    return create_item(id_user)


# obtener todos los artículos
@app.route('/items/<id_user>', methods=['GET'])
@token_required
def item_get_all_items(id_user):
    return get_all_items(id_user)


# obtener un artículo, filtrando por id
@app.route('/item/<id_user>/<id_item>', methods=['GET'])
@token_required
def item_get_one_item(id_user, id_item):
    return get_one_item(id_user, id_item)


# obtener los artículos, filtrando por descripción
@app.route('/item/description/<id_user>', methods=['POST'])
@token_required
def item_get_items_by_description(id_user):
    return get_items_by_description(id_user)


# eliminar un artículo, filtrando por id
@app.route('/item/<id_user>/<id_doc>', methods=['DELETE'])
@token_required
def item_delete_item(id_user, id_doc):
    return delete_item(id_user, id_doc)


# actualizar un artículo
@app.route('/item/<id_user>/<id_doc>', methods=['PUT'])
@token_required
def item_update_item(id_user, id_doc):
    return update_item(id_user, id_doc)


# añadir paquete a un artículo
@app.route('/item/<id_user>/<id_item>/<id_package>', methods=['PUT'])
@token_required
def item_add_package_to_item(id_user, id_item, id_package):
    return add_package_to_item(id_user, id_item, id_package)


# Ruta para realizar búsqueda avanzada de un artículo
@app.route('/item/search/<id_user>', methods=['POST'])
@token_required
def item_search_item(id_user):
    return search_item(id_user)
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
