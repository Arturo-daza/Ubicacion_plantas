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

def insercion_r (cliente, latitud, longitud, costo_servicio, costo) :

  con = conexion(DB_NAME=DB_NAME, DB_USER=DB_USER, DB_PASS=DB_PASS, DB_HOST=DB_HOST)
  cursor = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
  sql = f"INSERT INTO rectangular (cliente, latitud, longitud, carga, costo) VALUES('{cliente}','{latitud}','{longitud}', '{costo_servicio}', '{costo}')"
  cursor.execute(sql)
  #Comfirma los cambios en la base de datos
  con.commit() 
  cierre_conexion(con) 
  print("Registro ingresado satisfactoriamente")   

def update_r (cliente, latitud, longitud, costo_servicio, costo, id) :  
    con = conexion(DB_NAME=DB_NAME, DB_USER=DB_USER, DB_PASS=DB_PASS, DB_HOST=DB_HOST)
    cursor = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute("""
        UPDATE rectangular 
        SET cliente = %s,
            latitud = %s,
            longitud = %s,
            carga = %s,
            costo = %s
        WHERE id = %s
    """, (cliente, latitud, longitud, costo_servicio, costo,  id))
    con.commit()
    cierre_conexion(con)
 
def delete_r (id):
        con = conexion(DB_NAME=DB_NAME, DB_USER=DB_USER, DB_PASS=DB_PASS, DB_HOST=DB_HOST)
        cursor = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute('DELETE FROM rectangular  WHERE id = {0}'.format(id))
        con.commit()
        cierre_conexion(con)
        
        
# Truncar tabla
def truncar(tabla):
    con = conexion(DB_NAME=DB_NAME, DB_USER=DB_USER, DB_PASS=DB_PASS, DB_HOST=DB_HOST)
    cursor = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute(f'TRUNCATE TABLE {tabla}')
    con.commit()
    cierre_conexion(con)
    
# Ubicacion general

def u_consulta () :  
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

def u_get_id(id):
    con = conexion(DB_NAME=DB_NAME, DB_USER=DB_USER, DB_PASS=DB_PASS, DB_HOST=DB_HOST)
    cursor = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute('SELECT * FROM ubicacion WHERE id = %s', (id))
    data = cursor.fetchall()
    cierre_conexion(con) 
    return data 

def u_insercion (cliente, latitud, longitud, carga, costo) :

  con = conexion(DB_NAME=DB_NAME, DB_USER=DB_USER, DB_PASS=DB_PASS, DB_HOST=DB_HOST)
  cursor = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
  sql = f"INSERT INTO ubicacion(cliente, latitud, longitud, carga, costo) VALUES('{cliente}','{latitud}','{longitud}', '{carga}', '{costo}')"
  cursor.execute(sql)
  #Comfirma los cambios en la base de datos
  con.commit() 
  cierre_conexion(con) 
  print("Registro ingresado satisfactoriamente")   

def u_update (cliente, latitud, longitud, carga, costo, id) :  
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
 
def u_delete (id):
        con = conexion(DB_NAME=DB_NAME, DB_USER=DB_USER, DB_PASS=DB_PASS, DB_HOST=DB_HOST)
        cursor = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute('DELETE FROM ubicacion WHERE id = {0}'.format(id))
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
        carga = request.form['carga']
        costo = request.form['costo']
        u_insercion(cliente, latitud, longitud, carga, costo)
        flash('Registro añadido con exito')
        return redirect(url_for('rectangular'))

@app.route('/edit_r/<id>', methods = ['POST', 'GET'])
def get_employee_r(id):
    rectangular = get_id_r(id)
    return render_template('edit_rectangular.html', rectangular = rectangular[0])

@app.route('/update_r/<id>', methods=['POST'])
def update_register_r(id):
    if request.method == 'POST':
        cliente = request.form['cliente']
        latitud = request.form['latitud']
        longitud = request.form['longitud']
        carga = request.form['carga']
        costo = request.form['costo']
        
        update_r(cliente, latitud, longitud, carga, costo,  id)
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

@app.route('/ubicacion')
def ubicacion (): 
    list_users = u_consulta() 
    return render_template('ubicacion.html', list_users = list_users)

@app.route('/add_register_u', methods=['POST'])
def add_register_u():
    if request.method == 'POST':
        cliente = request.form['cliente']
        latitud = request.form['latitud']
        longitud = request.form['longitud']
        carga = request.form['carga']
        costo = request.form['costo']
        u_insercion(cliente, latitud, longitud, carga, costo)
        flash('Registro añadido con exito')
        return redirect(url_for('ubicacion'))

@app.route('/edit_u/<id>', methods = ['POST', 'GET'])
def get_employee_u(id):
    ubicacion = u_get_id(id)
    return render_template('edit_ubicacion.html', ubicacion = ubicacion[0])

@app.route('/update_u/<id>', methods=['POST'])
def update_register_u(id):
    if request.method == 'POST':
        cliente = request.form['cliente']
        latitud = request.form['latitud']
        longitud = request.form['longitud']
        carga = request.form['carga']
        costo = request.form['costo']
        
        update_r(cliente, latitud, longitud, carga, costo,  id)
        flash('Datos actualizados')
        return redirect(url_for('ubicacion'))


@app.route('/calcular_ubicacion', methods = ['POST','GET'])
def calcular_ubicacion(): 
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

@app.route('/delete_u/<string:id>', methods = ['POST','GET'])
def delete_register_u(id):
    u_delete(id)   
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
                u_insercion(row['cliente'], row['latitud'], row['longitud'], row['carga'], row['costo'])
        return redirect(url_for('ubicacion'))

if __name__ == "__main__":
    app.run(debug=True, port = 8500)