import math

def calcular_distancia(lat1, lon1, lat2, lon2):
    """
    Calcula la distancia en kilómetros entre dos puntos usando la fórmula de Haversine
    """
    # Radio de la Tierra en km
    R = 6371
    
    # Convertir grados a radianes
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    # Fórmula de Haversine
    a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    distancia = R * c
    return round(distancia, 2)


def calcular_costo_envio(distancia_km):
    """
    Calcula el costo de envío basado en la distancia
    
    Tarifas:
    - 0-5 km: Gratis (barrio cercano)
    - 5-10 km: $500
    - 10-20 km: $800
    - 20-30 km: $1200
    - 30+ km: $1500
    """
    if distancia_km <= 5:
        return 0
    elif distancia_km <= 10:
        return 500
    elif distancia_km <= 20:
        return 800
    elif distancia_km <= 30:
        return 1200
    else:
        return 1500


def obtener_coordenadas_desde_codigo_postal(codigo_postal):
    """
    Obtiene coordenadas aproximadas desde un código postal
    En producción, usarías una API como Google Maps Geocoding
    
    Por ahora, retorna coordenadas de ejemplo para Buenos Aires
    """
    # Coordenadas base (centro de Buenos Aires)
    coordenadas_base = {
        'C1000': (-34.6037, -58.3816),  # Centro
        'C1400': (-34.5895, -58.4173),  # Palermo
        'C1200': (-34.6158, -58.3974),  # Constitución
    }
    
    # Si el código postal está en la lista, retornar sus coordenadas
    for codigo, coords in coordenadas_base.items():
        if codigo_postal.startswith(codigo[:4]):
            return coords
    
    # Por defecto, retornar coordenadas del centro
    return (-34.6037, -58.3816)


# ✅ Para obtener coordenadas reales en producción, usar:
def obtener_coordenadas_google(direccion):
    """
    Obtiene coordenadas usando Google Maps Geocoding API
    Requiere: pip install googlemaps
    """
    import googlemaps
    from django.conf import settings
    
    try:
        gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)
        result = gmaps.geocode(direccion)
        
        if result:
            location = result[0]['geometry']['location']
            return (location['lat'], location['lng'])
    except:
        pass
    
    return None