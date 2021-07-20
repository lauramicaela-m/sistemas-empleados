from flask import Flask
from flask import render_template
from flask import request
from flask import redirect 
from flaskext.mysql import MySQL
from datetime import datetime
from pymysql import cursors
import os 

app = Flask(__name__)
mysql = MySQL()

app.config['MYSQL_DATABASE_HOST'] = 'db.wptcac.tk'
app.config['MYSQL_DATABASE_PORT'] = 15306
app.config['MYSQL_DATABASE_USER'] = 'fenunez'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'empleados'

UPLOADS = os.path.join('uploads')
app.config['UPLOADS'] = UPLOADS  #guardamos la ruta como un valor en la app

mysql.init_app(app)

@app.route('/')
def index():
    conn = mysql.connect()
    cursor = conn.cursor()

    sql = "SELECT * FROM empleados;"
    cursor.execute(sql)

    empleados = cursor.fetchall()
 
    conn.commit()

    return render_template('empleados/index.html', empleados=empleados)


@app.route('/create')
def create():
    
    return render_template('empleados/create.html')


@app.route('/store', methods=["POST"])
def store():
    _nombre = request.form['txtNombre']
    _correo = request.form['txtCorreo']
    _foto = request.files['txtFoto']

    now = datetime.now()
    print(now)
    tiempo = now.strftime("%Y%H%M%S")
    print(tiempo)

    if _foto.filename != '':
        nuevoNombreFoto = tiempo + '_' + _foto.filename
        _foto.save("source/uploads/"+ nuevoNombreFoto)


    sql = "INSERT INTO empleados (nombre, correo, foto) values (%s, %s, %s );"
    datos = (_nombre, _correo, nuevoNombreFoto)

    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql, datos)

    conn.commit()
    
    return redirect ('/')


@app.route('/delete/<int:id>')
def delete(id):
    conn = mysql.connect()
    cursor = conn.cursor()

    sql= f'SELECT foto FROM empleados WHERE id = "{id}"'
    cursor.execute(sql)

    nombreFoto = cursor.fetchone()[0]
    try:
        os.remove(os.path.join(app.config['UPLOADS'], nombreFoto))
    except:
        pass

    sql = f'DELETE FROM empleados WHERE id = {id}'
    cursor.execute(sql)

    conn.commit()
    
    
    return redirect('/')

@app.route('/modify/<int:id>')
def modify(id):
    sql = f'SELECT * FROM empleados WHERE id="{id}"'
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql)
    empleado = cursor.fetchone()
    conn.commit()

    return render_template('empleados/edit.html', empleado=empleado)

@app.route('/update', methods=['POST'])
def update():
    _nombre = request.form['txtNombre']
    _correo = request.form['txtCorreo']
    _foto = request.files['txtFoto']
    id = request.form['txtId']

    datos = (_nombre, _correo, id)

    conn = mysql.connect()
    cursor = conn.cursor()

    if _foto.filename != '':
        now= datetime.now()
        tiempo = now.strftime("%Y%H%M%S")
        nuevoNombreFoto = tiempo + '_' + _foto.filename
        _foto.save("source/uploads/" + nuevoNombreFoto)


        sql = f'SELECT foto FROM empleados WHERE id="{id}"'
        cursor.execute(sql)
        conn.commit()

        nombreFoto = cursor.fetchone()[0]
        borrarEstaFoto = os.path.join(app.config['UPLOADS'],nombreFoto)
        print(borrarEstaFoto)

        try:
            os.remove(os.path.join(app.config['UPLOADS'], nombreFoto))
        except: 
            pass

        sql= f'UPDATE empleados SET foto="{nuevoNombreFoto}" WHERE id="{id}";'
        cursor.execute(sql)
    
        
    sql = f'UPDATE empleados SET nombre="{_nombre}", correo="{_correo}" WHERE id="{id}"'
    cursor.execute(sql)
    conn.commit()

    return redirect ('/')





if __name__ == '__main__':
    app.run(debug=True)
