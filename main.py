from flask import Flask, render_template, request, redirect, url_for, flash
import psycopg2 #pip install psycopg2 
import psycopg2.extras
 
app = Flask(__name__)
app.secret_key = "cairocoders-ednalan"

## Datos para establecer la conexión a la base de datos
 
DB_HOST = "trumpet.db.elephantsql.com"
DB_NAME = "biwoqvym"
DB_USER = "biwoqvym"
DB_PASS = "SgxGYDFppxH471IfeWjelmoI_MrhlnZW"
 
## Crear una instacia que se conecte a la base de datos
conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
 
@app.route('/')
def Index():
    ## Se crea cursos para interactuar con la base de datos
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    # Se escribe la sentencia SQL
    s = "SELECT * FROM estudiantes"
    cur.execute(s) # Execute the SQL
    list_users = cur.fetchall() ## Para que muestre todos los resultados
    return render_template('index.html', list_users = list_users)
 
@app.route('/add_student', methods=['POST'])
def add_student():
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method == 'POST':
        nombre = request.form['nombre']
        codigo = request.form['codigo']
        email = request.form['email']
        cur.execute("INSERT INTO estudiantes (nombre, codigo, email) VALUES (%s,%s,%s)", (nombre, codigo, email))
        conn.commit()
        flash('Estudiante añadido con exito')
        return redirect(url_for('Index'))
 
@app.route('/edit/<id>', methods = ['POST', 'GET'])
def get_employee(id):
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
   
    cur.execute('SELECT * FROM estudiantes WHERE id = %s', (id))
    data = cur.fetchall()
    cur.close()
    print(data[0])
    return render_template('edit.html', student = data[0])
 
@app.route('/update/<id>', methods=['POST'])
def update_student(id):
    if request.method == 'POST':
        nombre = request.form['nombre']
        codigo = request.form['codigo']
        email = request.form['email']
         
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("""
            UPDATE estudiantes
            SET nombre = %s,
                codigo = %s,
                email = %s
            WHERE id = %s
        """, (nombre, codigo, email, id))
        flash('Datos del estudiante actualizados')
        conn.commit()
        return redirect(url_for('Index'))
 
@app.route('/delete/<string:id>', methods = ['POST','GET'])
def delete_student(id):
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
   
    cur.execute('DELETE FROM estudiantes WHERE id = {0}'.format(id))
    conn.commit()
    flash('Estudiante removido con exito')
    return redirect(url_for('Index'))
 
if __name__ == "__main__":
    app.run(debug=True, port = 8500)