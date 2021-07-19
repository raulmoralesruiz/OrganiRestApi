
from common_methods import *

# Conexión al servidor MongoDB
client = link_server()

# Conexión a la base de datos
db = client["organi"]

# Colección item
col_item = db.item_new

# Variable que indica el nombre/tipo del documento actual
doc_type = 'room'


# Método para obtener las habitaciones de los hogares
def get_all_rooms():
    section = 'room'

    # se obtiene la descripción (nombre) de la habitación
    description = request.json['description']

    # se define la query
    query = {'home.description': description}
    
    return get_section(col_item, section, query)