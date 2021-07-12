from common_methods import *

# Conexión al servidor MongoDB
client = link_server()

# Conexión a la base de datos
db = client["organi"]

# Colección container
col = db.container

# Variable que indica el nombre/tipo del documento actual
doc_type = 'container'


# Método para crear un contenedor
def create_container(id_room):
    col_father = db.room
    doc_type_father = 'room'
    son_schema = 'schemas/container/schema_container.json'
    doc_type_son = doc_type
    return create_document(id_room, col_father, doc_type_father, son_schema, col, doc_type_son)
    

# Método para obtener los contenedores con su habitación correspondiente
def get_container_with_room():
    father = 'room'
    return get_father_with_son(col, father)


# Método para obtener los contenedores
def get_all_containers():
    return get_all_documents(col)


# Método para obtener un contenedor
def get_one_container(id):
    return get_one_document(id, col)


# Método para obtener un contenedor filtrando por descripción
def get_containers_by_description():
    return get_documents_by_description(col)


# Método para eliminar un contenedor
def delete_container(id):
    doc_type = 'container'
    return delete_document(id, col, doc_type)


# Método para actualizar un contenedor
def update_container(id):
    doc_type = 'container'
    doc_schema_update = 'schemas/container/schema_container_update.json'
    return update_document(id, col, doc_type, doc_schema_update)