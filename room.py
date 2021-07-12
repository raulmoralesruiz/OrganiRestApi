from flask import jsonify, request

import bson
from bson.objectid import ObjectId

from common_methods import *


# Conexión al servidor MongoDB
client = link_server()

# Conexión a la base de datos
db = client["organi"]

# Variable para definir un acceso directo al documento de hogares (home)
col = db.room

# Variable que indica el nombre/tipo del documento actual
doc_type = 'room'

# Método para crear una habitación
def create_room(id_home):
    col_father = db.home
    doc_type_father = 'home'
    son_schema = 'schemas/room/schema_room.json'
    doc_type_son = 'room'
    return create_document(id_home, col_father, doc_type_father, son_schema, col, doc_type_son)
    

# Método para obtener las habitaciones con su hogar correspondiente
def get_room_with_home():
    father = 'home'
    return get_father_with_son(col, father)


# Método para obtener todas las habitaciones
def get_all_rooms():
    return get_all_documents(col)


# Método para obtener una habitación
def get_one_room(id):
    return get_one_document(id, col)


# Método para obtener una habitación filtrando por descripción
def get_rooms_by_description():
    return get_documents_by_description(col)


# Método para eliminar una habitación
def delete_room(id):
    return delete_document(id, col, doc_type)


# Método para actualizar un hogar
def update_room(id):
    doc_schema_update = 'schemas/room/schema_room_update.json'
    return update_document(id, col, doc_type, doc_schema_update)