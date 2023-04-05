import numpy as np 
import pandas as pd
import folium
import statistics
from math import radians, sin, cos, sqrt, atan2
from folium.plugins import HeatMap
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter



def convertir_df(data):
    data = pd.DataFrame(data)
    data.columns = ['id', 'cliente', 'latitud', 'longitud', 'carga', 'costo']
    lista= data.columns.to_list()
    del lista[0:2]

    for i in lista: 
        data[i]= data[i].astype(float)
    return data

def metodo_ubicacion_mapa(data):
    data = convertir_df(data)
    longs = data['longitud']
    lats = data['latitud']
    resultado, data = distancia_euclideana(data)
    localizacion_factible = get_address_from_coordinates(resultado['Factible']['Y'], resultado['Factible']['X'])
    localizacion_optimo = get_address_from_coordinates(resultado['Optimo']['Y'], resultado['Optimo']['X'])
    mapa = mapear(longs, lats, data, resultado['Factible'],resultado['Optimo'])
    return resultado, localizacion_factible, localizacion_optimo, mapa


def distancia_euclideana(data):
    data['cv']=data['carga']*data['costo']
    puntoFactibleX=(data['latitud']*data['carga']*data['costo']).sum()/(data['carga']*data['costo']).sum()
    puntoFactibleY=(data['longitud']*data['carga']*data['costo']).sum()/(data['carga']*data['costo']).sum()
    puntosFactibles={'X': puntoFactibleX, 'Y':puntoFactibleY}
    data['Indice euclideano']=np.sqrt(np.square(puntoFactibleX-data['latitud']) + np.square(puntoFactibleY-data['longitud']))
    CTT= (data['carga']*data['costo']*data['Indice euclideano']).sum()
    optimaX=(data['latitud']*data['carga']*data['costo']/data['Indice euclideano']).sum()/(data['carga']*data['costo']/data['Indice euclideano']).sum()
    optimaY=(data['longitud']*data['carga']*data['costo']/data['Indice euclideano']).sum()/(data['carga']*data['costo']/data['Indice euclideano']).sum()
    puntosOptimos={'X': optimaX, 'Y':optimaY}
    
    resultado = {'Factible': puntosFactibles,
                 'Optimo': puntosOptimos,
                 'CTT': CTT}
    
    return resultado, data

def get_address_from_coordinates(longitude, latitude):
    geolocator = Nominatim(user_agent='ccmexico')
    location = geolocator.reverse(f"{latitude}, {longitude}")
    return location.address

def mapear (longs, lats, data, factible, optimo):
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
                    radius=50, 
                    blur=50, 
                    max_zoom=1)

    #Creamos el marcador de Centro de Gravedad
    tooltip = 'Metodo distancia factible'
    folium.Marker([factible['X'], factible['Y']], popup="Punto factible", tooltip = tooltip).add_to(mapa)
    
    #Creamos el marcador de Centro de Gravedad
    tooltip = 'Metodo distancia optimo'
    folium.Marker([optimo['X'], optimo['Y']], popup="Punto optimo", tooltip = tooltip).add_to(mapa)
    
    # Agregar una línea entre los puntos
    distancia_km = calcular_distancia(factible['X'], factible['Y'], optimo['X'], optimo['Y'])
    folium.PolyLine(
        locations=[[factible['X'], factible['Y']], [optimo['X'], optimo['Y']]],
        color='blue',
        weight=5, 
        tooltip=f"Distancia: {distancia_km:.2f} km"
    ).add_to(mapa)

    # Adherimos la capa de mapa de calor al mapa principal
    mapa_calor.add_to(mapa)
    return mapa

def calcular_distancia(lat1, lon1, lat2, lon2):
    # Radio de la Tierra en km
    R = 6373.0

    # Convertir las coordenadas a radianes
    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)

    # Calcular la diferencia de longitud y latitud
    dlon = lon2 - lon1
    dlat = lat2 - lat1

    # Aplicar la fórmula de Haversine
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    # Calcular la distancia en km
    distancia = R * c

    return distancia