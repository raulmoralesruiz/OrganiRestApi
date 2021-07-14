from common_methods import *

# Conexión al servidor MongoDB
client = link_server()

# Conexión a la base de datos
db = client["organi"]

# Colección item
col_item = db.item_new

# Variable que indica el nombre/tipo del documento actual
doc_type = 'container'


# # Método para obtener los contenedores
# def get_all_containers():
#     return get_section(col_item, doc_type)


# Método para obtener las descripciones de los contenedores
def get_container_descriptions():
    section = 'container.description'
    return get_section(col_item, section)


# Método para obtener los colores de los contenedores
def get_container_colors():
    section = 'container.color'
    return get_section(col_item, section)