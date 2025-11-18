from pymongo import MongoClient
from django.conf import settings

def get_mongo_collection(collection_name):
    """
    Establece la conexión a MongoDB Atlas y retorna una colección específica.
    Usada para guardar geolocalización o logs.
    """
    # Verifica que la URI esté cargada
    if not settings.MONGO_ATLAS_URI:
        print("ERROR: MONGO_ATLAS_URI no está configurada en settings.")
        return None
        
    try:
        # 1. Conexión al cliente de MongoDB
        client = MongoClient(settings.MONGO_ATLAS_URI)
        
        # 2. Selecciona la base de datos (por defecto, la que está en la URI)
        db = client.get_database() 
        
        # 3. Retorna la colección solicitada
        return db[collection_name]
        
    except Exception as e:
        print(f"Error de conexión a MongoDB Atlas: {e}")
        return None