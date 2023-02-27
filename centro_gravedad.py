import pandas as pd
import numpy as np
import folium
import statistics
from folium.plugins import HeatMap
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter


def convertir_df(data):
    data = pd.DataFrame(data)
    data.columns = ['id', 'id_usuario', 'cliente', 'latitud', 'longitud', 'distribucion']
    return data

def metodo_centroide_con_mapa(data):
    ## Asegurar el tipo de datos, solo enviar numericos
    # Usar en caso de tener la longitud y logitud
    data = convertir_df(data)
    longs = data['longitud']
    lats = data['latitud']
    centro_gravedad = calcular_centro_gravedad(longs, lats, data)
    localizacion = get_address_from_coordinates(centro_gravedad['longs'], centro_gravedad['lats'])
    mapa = mapear(longs, lats, data, centro_gravedad)
    return centro_gravedad, localizacion, mapa

def metodo_centroide_con_mapa_direccion(data):
    ## Usar en caso de tener solo la ubicacion y no las coordenadas
    ## El df debe contener una columna con el pais, con la ciudad y con el lugar
    data = get_coordinates_from_address(data)
    longs, lats = extraer_coordenates(data)
    centro_gravedad = calcular_centro_gravedad(longs, lats, data)
    localizacion = get_address_from_coordinates(centro_gravedad['longs'], centro_gravedad['lats'])
    mapa = mapear(longs, lats, data,centro_gravedad)
    return centro_gravedad, localizacion, mapa
        
def calcular_centro_gravedad(longs, lats, data):
    # Series longs = Lista de las longitudes
    # Series lats = Lista de las latitudes
    # Data Frame data = Dataframe con los datos de la densidad, distribución, o peso, etc. 
    centro_gravedad = {}
    centro_gravedad['longs'] = np.dot(longs, data['distribucion']) / np.sum(data['distribucion'])
    centro_gravedad['lats'] = np.dot(lats, data['distribucion']) / np.sum(data['distribucion'])
    return centro_gravedad

def get_coordinates_from_address(data):
    # Estructura:
        # El df debe contener una columna con el pais, con la ciudad y con el lugar
    data["direccion"] = data["pais"] + ", " + data["ciudad"] + ", " + data["Institución / Lugar"]
    #Envíamos los datos a geocodificación
    servicio = Nominatim(user_agent="cctmexico")
    data["coordenadas"] = data["direccion"].apply(RateLimiter(servicio.geocode,min_delay_seconds=1))
    return data

def extraer_coordenates(data):
    # Se se usa el metodo get_coordenates_from_adreess usar este para sacar las coordenadas en una lista
    # Extraer las coordenadas de latitud y longitud en dos variables separadas (listas)
    longs = [coord.longitude for coord in data["coordenadas"]]
    lats = [coord.latitude for coord in data["coordenadas"]]
    return longs, lats

def get_address_from_coordinates(longitude, latitude):
    geolocator = Nominatim(user_agent='ccmexico')
    location = geolocator.reverse(f"{latitude}, {longitude}")
    return location.address


def mapear (longs, lats, data, centro_gravedad):
    # Series longs = Lista de las longitudes
    # Series lats = Lista de las latitudes
    # Data Frame data = Dataframe con los datos de la densidad, distribución, o peso, etc. 
    # dict centro de gravedad = con las coordenadas objetivos 
    # {'longs': -74.07947858972396, 'lats': 4.626305037613849}
    mediaLong = statistics.mean(longs)
    mediaLat = statistics.mean(lats)

    # Crear un objeto de mapa base Map()
    mapa = folium.Map(location=[mediaLat, mediaLong], zoom_start = 12)

    # Crear una capa de mapa de calor
    mapa_calor = HeatMap( list(zip(lats, longs, data['distribucion'])),
                    min_opacity=0.2,
                    max_val=data['distribucion'].max(),
                    radius=50, 
                    blur=50, 
                    max_zoom=1)

    #Creamos el marcador de Centro de Gravedad
    tooltip = 'Centro de gravedad'
    folium.Marker([centro_gravedad['lats'], centro_gravedad['longs']], popup="Centro", tooltip = tooltip).add_to(mapa)

    # Adherimos la capa de mapa de calor al mapa principal
    mapa_calor.add_to(mapa)
    return mapa

        