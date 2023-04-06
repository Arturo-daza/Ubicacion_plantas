import pandas as pd  
import numpy as np
import folium
import statistics
from folium.plugins import HeatMap
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

def convertir_df(data):
    data = pd.DataFrame(data)
    data.columns = ['id', 'id_usuario', 'cliente', 'latitud', 'longitud', 'cantidad_servicios', 'valor/servicio']
    return data

def metodo_rectangular_mapa(data):
    data = convertir_df(data)
    longs = data['longitud']
    lats = data['latitud']
    rectangular, data = calcular_metodo_rectangular(data)
    localizacion = get_address_from_coordinates(rectangular['longs'], rectangular['lats'])
    mapa = mapear(longs, lats, data, rectangular)
    return rectangular, localizacion, mapa

def calcular_metodo_rectangular(data):
    data["cv"]= data['cantidad_servicios']*data['valor/servicio']
    importancia_media = data['cv'].sum()/2
    
    df_lat = data[['cliente', 'latitud', 'cv']]
    df_lat =df_lat.sort_values(by = 'latitud')
    df_lat['acumulado']= df_lat.cv.cumsum()
    
    df_log = data[['cliente', 'longitud', 'cv']]
    df_log =df_log.sort_values(by = 'longitud')
    df_log['acumulado']= df_log.cv.cumsum()
    rectangular = {}
    rectangular['longs'] = df_log[df_log['acumulado']>importancia_media].iloc[0].to_list()[1]
    rectangular['lats'] = df_lat[df_lat['acumulado']>importancia_media].iloc[0].to_list()[1] 
    
    return rectangular, data

def get_address_from_coordinates(longitude, latitude):
    geolocator = Nominatim(user_agent='ccmexico')
    location = geolocator.reverse(f"{latitude}, {longitude}")
    return location.address

def mapear (longs, lats, data, rectangular):
    # Series longs = Lista de las longitudes
    # Series lats = Lista de las latitudes
    # Data Frame data = Dataframe con los datos de la densidad, distribuciÃ³n, o peso, etc. 
    # Densidad = Nombre de la columna donde esta el el peso distribuciÃ³n, etc
    # dict centro de gravedad = con las coordenadas objetivos 
    # {'longs': -74.07947858972396, 'lats': 4.626305037613849}
    mediaLong = statistics.mean(longs)
    mediaLat = statistics.mean(lats)

    # Crear un objeto de mapa base Map()
    mapa = folium.Map(location=[mediaLat, mediaLong], zoom_start = 12)

    # Crear una capa de mapa de calor
    mapa_calor = HeatMap( list(zip(lats, longs, data['cv'])),
                    min_opacity=0.2,
                    max_val=data['cv'].max(),
                    radius=50, 
                    blur=50, 
                    max_zoom=1)

    #Creamos el marcador de Centro de Gravedad
    tooltip = 'Metodo distancia rectangular'
    folium.Marker([rectangular['lats'], rectangular['longs']], popup="Punto trial", tooltip = tooltip).add_to(mapa)

    # Adherimos la capa de mapa de calor al mapa principal
    mapa_calor.add_to(mapa)
    return mapa