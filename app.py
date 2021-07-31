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
@token_required
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
            response["message"] = "Invalid email id"
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
    if len(password) >= 6 and len(password) <= 20 and any(char.isdigit() for char in password) \
        and any(char.isupper() for char in password) and any(char.islower() for char in password):
        return True
    else:
        return False


# @app.route("/test1")
# def test1():
#     item_archive = mongo.db.item_archive.find_one({})
#     response = json_util.dumps(item_archive)
#     return Response(response, mimetype='application/json')


# @app.route("/test2")
# @token_required
# def test2():
#     item_archive = mongo.db.item_archive.find_one({})
#     response = json_util.dumps(item_archive)
#     return Response(response, mimetype='application/json')


""" -------------------- HOME - START -------------------- """
# Ruta para obtener los hogares
@app.route('/homes', methods=['GET'])
@token_required
def home_get_all_homes():
    return get_all_homes()
""" -------------------- HOME - END -------------------- """


""" -------------------- ROOM - START -------------------- """
# Ruta para obtener las habitaciones
@app.route('/rooms', methods=['POST'])
@token_required
def room_get_all_rooms():
    return get_all_rooms()
""" -------------------- ROOM - END -------------------- """


""" -------------------- CONTAINER - START -------------------- """
# Ruta para obtener los contenedores
@app.route('/containers', methods=['POST'])
@token_required
def container_get_all_containers():
    return get_all_containers()
""" -------------------- CONTAINER - END -------------------- """


""" -------------------- COMPARTMENT - START -------------------- """
# Ruta para obtener los compartimentos
@app.route('/compartments', methods=['POST'])
@token_required
def compartment_get_all_compartments():
    return get_all_compartments()
""" -------------------- COMPARTMENT - END -------------------- """


""" -------------------- ITEM - START -------------------- """
# crear un artículo
@app.route('/item', methods=['POST'])
@token_required
def item_create_item():
    return create_item()


# obtener todos los artículos
@app.route('/items', methods=['GET'])
@token_required
def item_get_all_items():
    return get_all_items()


# obtener un artículo, filtrando por id
@app.route('/item/<id_item>', methods=['GET'])
@token_required
def item_get_one_item(id_item):
    return get_one_item(id_item)


# obtener los artículos, filtrando por descripción
@app.route('/item/description', methods=['POST'])
@token_required
def item_get_items_by_description():
    return get_items_by_description()


# eliminar un artículo, filtrando por id
@app.route('/item/<id>', methods=['DELETE'])
@token_required
def item_delete_item(id):
    return delete_item(id)


# actualizar un artículo
@app.route('/item/<id>', methods=['PUT'])
@token_required
def item_update_item(id):
    return update_item(id)


# añadir paquete a un artículo
@app.route('/item/<id_item>/<id_package>', methods=['PUT'])
@token_required
def item_add_package_to_item(id_item, id_package):
    return add_package_to_item(id_item, id_package)


# Ruta para realizar búsqueda avanzada de un artículo
@app.route('/item/search', methods=['POST'])
@token_required
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
