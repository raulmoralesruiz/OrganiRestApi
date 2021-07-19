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
def get_all_homes():
    section = 'home'
    query = {}
    return get_section(col_item, section, query)