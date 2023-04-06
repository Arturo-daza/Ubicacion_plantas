import pandas as pd
import numpy as np
import folium
import statistics
from folium.plugins import HeatMap
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from math import radians, sin, cos, sqrt, atan2


class UbicacionPlanta: 
    def __init__(self, data):
        self.data= pd.DataFrame(data)
        self.data.columns = ['id', 'cliente', 'latitud', 'longitud', 'carga', 'costo']
        self.data[['latitud', 'longitud', 'carga', 'costo']]= self.data[['latitud', 'longitud', 'carga', 'costo']].astype(float)
        self.longs = self.data['longitud']
        self.lats = self.data['latitud']
        self.data["cv"]= self.data['carga']*self.data['costo']
        self.centro_gravedad = {}
        self.localizacion_centro_gravedad ="si"
        self.rectangular = {}
        self.localizacion_rectangular =""
        self.euclideana={}
        self.localizacion_euclideana_optima =""
        self.localizacion_euclideana_factible =""

    def calcular_centro_gravedad(self):
        # Series longs = Lista de las longitudes
        # Series lats = Lista de las latitudes
        # Data Frame data = Dataframe con los datos de la densidad, distribución, o peso, etc. 
        self.centro_gravedad['longs'] = np.dot(self.longs, self.data['carga']) / np.sum(self.data['carga'])
        self.centro_gravedad['lats'] = np.dot(self.lats, self.data['carga']) / np.sum(self.data['carga'])
        
    def calcular_metodo_rectangular(self):
        importancia_media = self.data['cv'].sum()/2
        
        df_lat = self.data[['cliente', 'latitud', 'cv']]
        df_lat =df_lat.sort_values(by = 'latitud')
        df_lat['acumulado']= df_lat.cv.cumsum()
        
        df_log = self.data[['cliente', 'longitud', 'cv']]
        df_log =df_log.sort_values(by = 'longitud')
        df_log['acumulado']= df_log.cv.cumsum()
        
        self.rectangular['longs'] = df_log[df_log['acumulado']>importancia_media].iloc[0].to_list()[1]
        self.rectangular['lats'] = df_lat[df_lat['acumulado']>importancia_media].iloc[0].to_list()[1] 
        
    def distancia_euclideana(self):
        self.data['cv']=self.data['carga']*self.data['costo']
        puntoFactibleX=(self.data['latitud']*self.data['carga']*self.data['costo']).sum()/(self.data['carga']*self.data['costo']).sum()
        puntoFactibleY=(self.data['longitud']*self.data['carga']*self.data['costo']).sum()/(self.data['carga']*self.data['costo']).sum()
        puntosFactibles={'X': puntoFactibleX, 'Y':puntoFactibleY}
        self.data['Indice euclideano']=np.sqrt(np.square(puntoFactibleX-self.data['latitud']) + np.square(puntoFactibleY-self.data['longitud']))
        CTT= (self.data['carga']*self.data['costo']*self.data['Indice euclideano']).sum()
        optimaX=(self.data['latitud']*self.data['carga']*self.data['costo']/self.data['Indice euclideano']).sum()/(self.data['carga']*self.data['costo']/self.data['Indice euclideano']).sum()
        optimaY=(self.data['longitud']*self.data['carga']*self.data['costo']/self.data['Indice euclideano']).sum()/(self.data['carga']*self.data['costo']/self.data['Indice euclideano']).sum()
        puntosOptimos={'X': optimaX, 'Y':optimaY}
        
        self.euclideana = {'Factible': puntosFactibles,
                    'Optimo': puntosOptimos}

    def metodo_centroide_mapa(self):
        ## Asegurar el tipo de datos, solo enviar numericos
        # Usar en caso de tener la longitud y logitud
        self.calcular_centro_gravedad()
        self.localizacion_centro_gravedad = get_address_from_coordinates(self.centro_gravedad['longs'], self.centro_gravedad['lats'])
        mapa = self.mapear("gravedad")
        return mapa
    
    def metodo_rectangular_mapa(self):
        self.calcular_metodo_rectangular()
        self.localizacion_rectangular = get_address_from_coordinates(self.rectangular['longs'], self.rectangular['lats'])
        mapa = self.mapear("rectangular")
        return mapa
    
    def metodo_euclideano_mapa(self):
        self.distancia_euclideana()
        self.localizacion_euclideana_factible = get_address_from_coordinates(self.euclideana['Factible']['Y'], self.euclideana['Factible']['X'])
        self.localizacion_euclideana_optima = get_address_from_coordinates(self.euclideana['Optimo']['Y'], self.euclideana['Optimo']['X'])
        mapa = self.mapear("euclideano")
        return mapa
    
    def metodos_unificados_mapa(self):
        self.calcular_centro_gravedad()
        self.calcular_metodo_rectangular()
        self.distancia_euclideana()
        self.localizacion_centro_gravedad = get_address_from_coordinates(self.centro_gravedad['longs'], self.centro_gravedad['lats'])
        self.localizacion_rectangular = get_address_from_coordinates(self.rectangular['longs'], self.rectangular['lats'])
        self.localizacion_euclideana_factible = get_address_from_coordinates(self.euclideana['Factible']['Y'], self.euclideana['Factible']['X'])
        self.localizacion_euclideana_optima = get_address_from_coordinates(self.euclideana['Optimo']['Y'], self.euclideana['Optimo']['X'])
        mapa = self.mapear("todo")
        return mapa
        
        
    def mapear (self, metodo):
        # Series longs = Lista de las longitudes
        # Series lats = Lista de las latitudes
        # Data Frame data = Dataframe con los datos de la densidad, distribución, o peso, etc. 
        # dict centro de gravedad = con las coordenadas objetivos 
        # {'longs': -74.07947858972396, 'lats': 4.626305037613849}
        # https://getbootstrap.com/docs/3.3/components/ para los iconos
        mediaLong = statistics.mean(self.longs)
        mediaLat = statistics.mean(self.lats)

        # Crear un objeto de mapa base Map()
        mapa = folium.Map(location=[mediaLat, mediaLong], zoom_start = 5)

        # Crear una capa de mapa de calor
        mapa_calor = HeatMap( list(zip(self.lats, self.longs, self.data['carga'])),
                        min_opacity=0.2,
                        radius=50, 
                        blur=50, 
                        max_zoom=1)
        #prub

        #Creamos el marcador de Centro de Gravedad
        if metodo== "gravedad":
            tooltip = 'Centro de gravedad'
            folium.Marker([self.centro_gravedad['lats'], self.centro_gravedad['longs']], popup="Centro de gravedad", tooltip = tooltip).add_to(mapa)
        elif metodo == "rectangular":
            tooltip = 'Metodo rectangular'
            folium.Marker([self.rectangular['lats'], self.rectangular['longs']], popup="Metodo rectangular", tooltip = tooltip).add_to(mapa)
        elif metodo=="euclideano": 
            longs=[]
            lats=[]
            nombre=["Punto factible", "Punto optimo"]
            for i in self.euclideana.values():
                longs.append(i["X"])
                lats.append(i["Y"])
            
            for i in range(2):
                tooltip = nombre[i]
                folium.Marker(
                    [longs[i], lats[i]], 
                    tooltip = tooltip, 
                    icon=folium.Icon(color="red", icon="info-sign")
                ).add_to(mapa)
            distancia_km = calcular_distancia(longs[0], lats[0], longs[1], lats[1])
            folium.PolyLine(
                locations=[[longs[0], lats[0]], [longs[1], lats[1]]],
                color='red',
                weight=5, 
                tooltip=f"Distancia: {distancia_km:.2f} km"
            ).add_to(mapa)
        else: 
            tooltip = 'Centro de gravedad'
            folium.Marker([self.centro_gravedad['lats'],
                           self.centro_gravedad['longs']], 
                           popup="Centro de gravedad", 
                           tooltip = tooltip,
                           icon=folium.Icon(color="green", icon="glyphicon glyphicon-hand-down")
                ).add_to(mapa)
            tooltip = 'Metodo rectangular'
            folium.Marker([self.rectangular['lats'], 
                           self.rectangular['longs']], 
                          popup="Metodo rectangular", 
                          tooltip = tooltip, 
                          icon=folium.Icon(color="blue", icon="glyphicon glyphicon-pushpin")
                ).add_to(mapa)
            longs=[]
            lats=[]
            nombre=["Punto factible", "Punto optimo"]
            for i in self.euclideana.values():
                longs.append(i["X"])
                lats.append(i["Y"])
            
            for i in range(2):
                tooltip = nombre[i]
                folium.Marker(
                    [longs[i], lats[i]], 
                    tooltip = tooltip, 
                    icon=folium.Icon(color="red", icon="glyphicon glyphicon-fire")
                ).add_to(mapa)
            distancia_km = calcular_distancia(longs[0], lats[0], longs[1], lats[1])
            folium.PolyLine(
                locations=[[longs[0], lats[0]], [longs[1], lats[1]]],
                color='red',
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

def get_address_from_coordinates(longitude, latitude):
        geolocator = Nominatim(user_agent='my_app', timeout=10)
        location = geolocator.reverse(f"{latitude}, {longitude}")
        
        return location.address