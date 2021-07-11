from common_methods import *

# Conexión al servidor MongoDB
client = link_server()

# Conexión a la base de datos
db = client["organi"]

# Colección home
col = db.home

# Variable que indica el nombre/tipo del documento actual
doc_type = 'home'


# Método para crear un hogar
def create_home():
    doc_schema = 'schemas/home/schema_home.json'
    id_father = None
    doc_type_father = None
    return insert_document(doc_schema, col, doc_type, id_father, doc_type_father)


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
    return delete_document(id, col, doc_type)


# Método para actualizar un hogar
def update_home(id):
    doc_schema_update = 'schemas/home/schema_home_update.json'
    return update_document(id, col, doc_type, doc_schema_update)