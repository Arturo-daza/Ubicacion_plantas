from flask import Flask, render_template, request, redirect, url_for, flash
import psycopg2 #pip install psycopg2 
import psycopg2.extras
from psycopg2 import Error
from centro_gravedad import metodo_centroide_con_mapa, convertir_df
from distancia_rectangular import metodo_rectangular_mapa
from ubicacion import metodo_ubicacion_mapa

from objeto import UbicacionPlanta as up
import pandas as pd
 
app = Flask(__name__)
app.config['ENV'] = 'development'
app.secret_key = "cairocoders-ednalan"

## Datos para establecer la conexión a la base de datos
 
DB_HOST = "trumpet.db.elephantsql.com"
DB_NAME = "biwoqvym"
DB_USER = "biwoqvym"
DB_PASS = "SgxGYDFppxH471IfeWjelmoI_MrhlnZW"
 
## Crear una instacia que se conecte a la base de datos


conexion = None
#Establecer conexion
def conexion(DB_HOST, DB_NAME, DB_USER, DB_PASS):
  try:
    con = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
  except Error as e:
    print("Error al establecer conexión: ",e)
  return con 

#Cierre conexion
def cierre_conexion(con):
    try:
        con.close()
    except Error as e:
        print('Se ha presentado error al cerrar la conexion')

# Truncar tabla
def truncar(tabla):
    con = conexion(DB_NAME=DB_NAME, DB_USER=DB_USER, DB_PASS=DB_PASS, DB_HOST=DB_HOST)
    cursor = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute(f'TRUNCATE TABLE {tabla}')
    con.commit()
    cierre_conexion(con)
    
# consulta a la base de datos
def consulta () :  
  #Consulta de datos 
    resultado = None
    try:
        con = conexion(DB_NAME=DB_NAME, DB_USER=DB_USER, DB_PASS=DB_PASS, DB_HOST=DB_HOST)
        cursor = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute('SELECT * FROM ubicacion')
        resultado = cursor.fetchall()
        cierre_conexion(con)        
    except Error as e:
        print(f'Se ha presentado un error al consultar:{e}')
    return resultado

def get_id(id):
    con = conexion(DB_NAME=DB_NAME, DB_USER=DB_USER, DB_PASS=DB_PASS, DB_HOST=DB_HOST)
    cursor = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute('SELECT * FROM ubicacion WHERE id = %s', (id))
    data = cursor.fetchall()
    cierre_conexion(con) 
    return data 

def insercion (cliente, latitud, longitud, carga, costo) :

  con = conexion(DB_NAME=DB_NAME, DB_USER=DB_USER, DB_PASS=DB_PASS, DB_HOST=DB_HOST)
  cursor = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
  sql = f"INSERT INTO ubicacion(cliente, latitud, longitud, carga, costo) VALUES('{cliente}','{latitud}','{longitud}', '{carga}', '{costo}')"
  cursor.execute(sql)
  #Comfirma los cambios en la base de datos
  con.commit() 
  cierre_conexion(con) 
  print("Registro ingresado satisfactoriamente")   

def update (cliente, latitud, longitud, carga, costo, id) :  
    con = conexion(DB_NAME=DB_NAME, DB_USER=DB_USER, DB_PASS=DB_PASS, DB_HOST=DB_HOST)
    cursor = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute("""
        UPDATE ubicacion
        SET cliente = %s,
            latitud = %s,
            longitud = %s,
            carga = %s, 
            costo = %s
        WHERE id = %s
    """, (cliente, latitud, longitud, carga, costo, id))
    con.commit()
    cierre_conexion(con)
 
def delete (id):
        con = conexion(DB_NAME=DB_NAME, DB_USER=DB_USER, DB_PASS=DB_PASS, DB_HOST=DB_HOST)
        cursor = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute('DELETE FROM ubicacion WHERE id = {0}'.format(id))
        con.commit()
        cierre_conexion(con)
        
@app.route('/')
def Index():
    return render_template('index.html')


@app.route('/ubicacion')
def ubicacion (): 
    list_users = consulta() 
    return render_template('ubicacion.html', list_users = list_users)

@app.route('/add_register_u', methods=['POST'])
def add_register_u():
    if request.method == 'POST':
        cliente = request.form['cliente']
        latitud = request.form['latitud']
        longitud = request.form['longitud']
        carga = request.form['carga']
        costo = request.form['costo']
        insercion(cliente, latitud, longitud, carga, costo)
        flash('Registro añadido con exito')
        return redirect(url_for('ubicacion'))

@app.route('/edit_u/<id>', methods = ['POST', 'GET'])
def get_employee_u(id):
    ubicacion = get_id(id)
    return render_template('edit_ubicacion.html', ubicacion = ubicacion[0])

@app.route('/update_u/<id>', methods=['POST'])
def update_register_u(id):
    if request.method == 'POST':
        cliente = request.form['cliente']
        latitud = request.form['latitud']
        longitud = request.form['longitud']
        carga = request.form['carga']
        costo = request.form['costo']
        
        update(cliente, latitud, longitud, carga, costo,  id)
        flash('Datos actualizados')
        return redirect(url_for('ubicacion'))



@app.route('/delete_u/<string:id>', methods = ['POST','GET'])
def delete_register_u(id):
    delete(id)   
    flash('Registro removido con exito')
    return redirect(url_for('ubicacion'))

@app.route('/subir_csv', methods=['POST'])
def subir_csv():
    import io
    if request.method == 'POST':
        archivo = request.files['archivo_csv']
        if archivo: 
            df = pd.read_csv(io.StringIO(archivo.read().decode('utf-8')), sep=";", decimal=",")
            truncar('ubicacion')
            for index, row in df.iterrows():
                insercion(row['cliente'], row['latitud'], row['longitud'], row['carga'], row['costo'])
        return redirect(url_for('ubicacion'))


@app.route('/calcular_ubicacion', methods = ['POST','GET'])
def calcular_ubicacion(): 
    
    ubicacionPlanta= up(consulta())
    mapa = ubicacionPlanta.metodos_unificados_mapa()
    resultado = ubicacionPlanta.euclideana
        # set the iframe width and height
    mapa.get_root().width = "800px"
    mapa.get_root().height = "600px"
    iframe = mapa.get_root()._repr_html_()
    context = {
        'resultado_factible': resultado['Factible'], 
        'resultado_optimo': resultado['Optimo'], 
        'rectangular': ubicacionPlanta.rectangular, 
        'centro_gravedad':ubicacionPlanta.centro_gravedad,
        'localizacion_factible': ubicacionPlanta.localizacion_euclideana_factible, 
        'localizacion_optimo': ubicacionPlanta.localizacion_euclideana_optima, 
        'localizacion_rectangular': ubicacionPlanta.localizacion_rectangular,
        'localizacion_centro_gravedad': ubicacionPlanta.localizacion_centro_gravedad, 
        'iframe':iframe
    }
    return render_template('calculo_ubicacion.html', **context)

if __name__ == "__main__":
    app.run(debug=True, port = 8500)