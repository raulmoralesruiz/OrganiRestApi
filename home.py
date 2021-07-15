from common_methods import *

# Conexión al servidor MongoDB
client = link_server()

# Conexión a la base de datos
db = client["organi"]

# Colección item
col_item = db.item_new

# Variable que indica el nombre/tipo del documento actual
doc_type = 'home'


# Método para obtener las descripciones de los hogares
def get_home_descriptions():
    section = 'home.description'
    return get_section(col_item, section)


# Método para obtener las direcciones de los hogares
def get_home_addresses():
    section = 'home.address'
    return get_section(col_item, section)