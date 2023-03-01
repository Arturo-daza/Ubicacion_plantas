from flask import Flask, render_template, request, redirect, url_for, flash
import psycopg2 #pip install psycopg2 
import psycopg2.extras
from psycopg2 import Error
from centro_gravedad import metodo_centroide_con_mapa, convertir_df
from distancia_rectangular import metodo_rectangular_mapa
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

def consulta () :  
  #Consulta de datos 
    resultado = None
    try:
        con = conexion(DB_NAME=DB_NAME, DB_USER=DB_USER, DB_PASS=DB_PASS, DB_HOST=DB_HOST)
        cursor = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute('SELECT * FROM centroide')
        resultado = cursor.fetchall()
        cierre_conexion(con)        
    except Error as e:
        print(f'Se ha presentado un error al consultar la tabla de parametros_produccion:{e}')
    return resultado

def get_id(id):
    con = conexion(DB_NAME=DB_NAME, DB_USER=DB_USER, DB_PASS=DB_PASS, DB_HOST=DB_HOST)
    cursor = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute('SELECT * FROM centroide WHERE id = %s', (id))
    data = cursor.fetchall()
    cierre_conexion(con) 
    return data 

def insercion (cliente, latitud, longitud, distribucion) :

  con = conexion(DB_NAME=DB_NAME, DB_USER=DB_USER, DB_PASS=DB_PASS, DB_HOST=DB_HOST)
  cursor = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
  sql = f"INSERT INTO centroide(cliente, latitud, longitud, distribucion) VALUES('{cliente}','{latitud}','{longitud}', '{distribucion}')"
  cursor.execute(sql)
  #Comfirma los cambios en la base de datos
  con.commit() 
  cierre_conexion(con) 
  print("Registro ingresado satisfactoriamente")   

def update (cliente, latitud, longitud, distribucion, id) :  
    con = conexion(DB_NAME=DB_NAME, DB_USER=DB_USER, DB_PASS=DB_PASS, DB_HOST=DB_HOST)
    cursor = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute("""
        UPDATE centroide
        SET cliente = %s,
            latitud = %s,
            longitud = %s,
            distribucion = %s
        WHERE id = %s
    """, (cliente, latitud, longitud, distribucion, id))
    con.commit()
    cierre_conexion(con)
 
def delete (id):
        con = conexion(DB_NAME=DB_NAME, DB_USER=DB_USER, DB_PASS=DB_PASS, DB_HOST=DB_HOST)
        cursor = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute('DELETE FROM centroide WHERE id = {0}'.format(id))
        con.commit()
        cierre_conexion(con)
        
        
def consulta_r () :  
  #Consulta de datos 
    resultado = None
    try:
        con = conexion(DB_NAME=DB_NAME, DB_USER=DB_USER, DB_PASS=DB_PASS, DB_HOST=DB_HOST)
        cursor = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute('SELECT * FROM rectangular')
        resultado = cursor.fetchall()
        cierre_conexion(con)        
    except Error as e:
        print(f'Se ha presentado un error al consultar la tabla de parametros_produccion:{e}')
    return resultado

def get_id_r(id):
    con = conexion(DB_NAME=DB_NAME, DB_USER=DB_USER, DB_PASS=DB_PASS, DB_HOST=DB_HOST)
    cursor = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute('SELECT * FROM rectangular  WHERE id = %s', (id))
    data = cursor.fetchall()
    cierre_conexion(con) 
    return data 

def insercion_r (cliente, latitud, longitud, cantidad_servicio, valor) :

  con = conexion(DB_NAME=DB_NAME, DB_USER=DB_USER, DB_PASS=DB_PASS, DB_HOST=DB_HOST)
  cursor = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
  sql = f"INSERT INTO rectangular (cliente, latitud, longitud, cantidad_servicios, valor) VALUES('{cliente}','{latitud}','{longitud}', '{cantidad_servicio}', '{valor}')"
  cursor.execute(sql)
  #Comfirma los cambios en la base de datos
  con.commit() 
  cierre_conexion(con) 
  print("Registro ingresado satisfactoriamente")   

def update_r (cliente, latitud, longitud, cantidad_servicio, valor, id) :  
    con = conexion(DB_NAME=DB_NAME, DB_USER=DB_USER, DB_PASS=DB_PASS, DB_HOST=DB_HOST)
    cursor = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute("""
        UPDATE rectangular 
        SET cliente = %s,
            latitud = %s,
            longitud = %s,
            cantidad_servicios = %s,
            valor = %s
        WHERE id = %s
    """, (cliente, latitud, longitud, cantidad_servicio, valor,  id))
    con.commit()
    cierre_conexion(con)
 
def delete_r (id):
        con = conexion(DB_NAME=DB_NAME, DB_USER=DB_USER, DB_PASS=DB_PASS, DB_HOST=DB_HOST)
        cursor = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute('DELETE FROM rectangular  WHERE id = {0}'.format(id))
        con.commit()
        cierre_conexion(con)
        
@app.route('/')
def Index():
    return render_template('index.html')

@app.route('/centroide')
def centroide (): 
    list_users = consulta() 
    return render_template('centro_gravedad.html', list_users = list_users)
 
@app.route('/add_register', methods=['POST'])
def add_register():
    if request.method == 'POST':
        cliente = request.form['cliente']
        latitud = request.form['latitud']
        longitud = request.form['longitud']
        distribucion = request.form['distribucion']
        insercion(cliente, latitud, longitud, distribucion)
        flash('Registro añadido con exito')
        return redirect(url_for('centroide'))
 
@app.route('/edit/<id>', methods = ['POST', 'GET'])
def get_employee(id):
    data = get_id(id)
    print(data[0])
    return render_template('edit.html', centroide = data[0])


 
@app.route('/update/<id>', methods=['POST'])
def update_register(id):
    if request.method == 'POST':
        cliente = request.form['cliente']
        latitud = request.form['latitud']
        longitud = request.form['longitud']
        distribucion = request.form['distribucion']
        
        update(cliente, latitud, longitud, distribucion, id)
        flash('Datos actualizados')
        return redirect(url_for('centroide'))
 
@app.route('/delete/<string:id>', methods = ['POST','GET'])
def delete_student(id):
    delete(id)   
    flash('Registro removido con exito')
    return redirect(url_for('centroide'))
 
@app.route('/calcular', methods = ['POST','GET'])
def calcular(): 
    centro_gravedad, localizacion, mapa = metodo_centroide_con_mapa(consulta())
    # set the iframe width and height
    mapa.get_root().width = "800px"
    mapa.get_root().height = "600px"
    iframe = mapa.get_root()._repr_html_()
    context = {
        'centro_gravedad': centro_gravedad, 
        'localizacion': localizacion, 
        'iframe':iframe
    }
    return render_template('centroide.html', **context)

@app.route('/rectangular')
def rectangular (): 
    list_users = consulta_r() 
    return render_template('rectangular.html', list_users = list_users)

@app.route('/add_register_r', methods=['POST'])
def add_register_r():
    if request.method == 'POST':
        cliente = request.form['cliente']
        latitud = request.form['latitud']
        longitud = request.form['longitud']
        cantidad_servicios = request.form['cantidad_servicios']
        valor = request.form['valor/servicio']
        insercion_r(cliente, latitud, longitud, cantidad_servicios, valor)
        flash('Registro añadido con exito')
        return redirect(url_for('rectangular'))

@app.route('/edit_r/<id>', methods = ['POST', 'GET'])
def get_employee_r(id):
    rectangular = get_id_r(id)
    print(rectangular[0])
    return render_template('edit_rectangular.html', rectangular = rectangular[0])

@app.route('/update_r/<id>', methods=['POST'])
def update_register_r(id):
    if request.method == 'POST':
        cliente = request.form['cliente']
        latitud = request.form['latitud']
        longitud = request.form['longitud']
        cantidad_servicios = request.form['cantidad_servicios']
        valor = request.form['valor']
        
        update_r(cliente, latitud, longitud, cantidad_servicios, valor,  id)
        flash('Datos actualizados')
        return redirect(url_for('rectangular'))


@app.route('/calcular_distancia_rectangular', methods = ['POST','GET'])
def calcular_distancia_rectangular(): 
    rectangular, localizacion, mapa = metodo_rectangular_mapa(consulta_r())
    # set the iframe width and height
    mapa.get_root().width = "800px"
    mapa.get_root().height = "600px"
    iframe = mapa.get_root()._repr_html_()
    context = {
        'rectangular': rectangular, 
        'localizacion': localizacion, 
        'iframe':iframe
    }
    return render_template('calculo_rectangular.html', **context)

@app.route('/delete_r/<string:id>', methods = ['POST','GET'])
def delete_register_r(id):
    delete_r(id)   
    flash('Registro removido con exito')
    return redirect(url_for('rectangular'))
if __name__ == "__main__":
    app.run(debug=True, port = 8500)