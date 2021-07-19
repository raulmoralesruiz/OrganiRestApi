from common_methods import *

# Conexión al servidor MongoDB
client = link_server()

# Conexión a la base de datos
db = client["organi"]

# Colección item
col_item = db.item_new

# Variable que indica el nombre/tipo del documento actual
doc_type = 'container'


# Método para obtener las direcciones de los hogares
def get_all_containers():
    section = 'container'

    # se obtiene la descripción (nombre) del hogar
    home = request.json['home']

    # se obtiene la descripción (nombre) de la habitación
    room = request.json['room']

    # se define la query
    query = {'home.description': home, 'room.description': room}
    
    return get_section(col_item, section, query)