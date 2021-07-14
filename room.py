
from common_methods import *

# Conexión al servidor MongoDB
client = link_server()

# Conexión a la base de datos
db = client["organi"]

# Colección item
col_item = db.item_new

# Variable que indica el nombre/tipo del documento actual
doc_type = 'room'


# Método para obtener todas las habitaciones
def get_all_rooms():
    section = 'room.description'
    return get_section(col_item, section)