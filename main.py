from flask import Flask,render_template,url_for,redirect,request,flash,session
from flask_mysqldb import MySQL
from config import config
app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'gr3g0r1j053y3p3z4rt34g4'
app.config['MYSQL_DB'] = 'master_python'

app.secret_key = '123456'
conexion = MySQL(app)

@app.route('/')
def index():
    return redirect(url_for('singin'))


@app.route('/singin', methods=['GET','POST'])
def singin():
    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        cursor = conexion.connection.cursor()
        cursor.execute(f'SELECT nombreUser,emailUser,passUser FROM usuarios;')
        usuarios =  cursor.fetchall()
        for user in usuarios:
            if user[1] == email and user[2] == password:
                session['username'] = user[0]
                session['email'] = user[1]
                return redirect(url_for('home'))
        flash('Username o password invalidos')
    return render_template('auth/singin.html') 


@app.route('/singup', methods=['GET','POST'])
def singup():
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        email = request.form['email']
        password = request.form['password']

        cursor = conexion.connection.cursor()
        cursor.execute(f'SELECT emailUser,passUser FROM usuarios')
        usuarios =  cursor.fetchall()
        for user in usuarios:
            if user[0] == email and user[1] == password:
                flash('El email o el password ya está en uso por otro usuario')
                
                return render_template('auth/singup.html',error=True)
            
        cursor.execute(f'INSERT INTO usuarios (nombreUser,apellidoUser,emailUser,passUser,fecharegistro) values("{nombre}","{apellido}","{email}","{password}",CURDATE());')
        conexion.connection.commit ()
        flash('Usuario Registrado exitosamente!!')

    return render_template('auth/singup.html')

@app.route('/home')
def home():

    emailUser = session['email']

    cursor = conexion.connection.cursor()
    cursor.execute(f'SELECT idUser FROM usuarios WHERE emailUser = "{emailUser}"')
    idUser = cursor.fetchone()
        
    cursor.execute(f'SELECT idnotas,tituloNota,conteNota FROM notas WHERE idUser = {idUser[0]}')
    campos = cursor.fetchall()
    if campos:
        print('Algo')
    else:
        print('vacio')    
    return render_template('session/home.html',nombre=session['username'],campos=campos)

@app.route('/createNote', methods=['GET','POST'])
def createNote():
    if request.method == 'POST':
        tituloNota = request.form['tituloNota']
        contenidoNota = request.form['contenidoNota']
        emailUser = session['email']
        cursor = conexion.connection.cursor()
        cursor.execute(f'SELECT idUser FROM usuarios WHERE emailUser = "{emailUser}"')
        idUser = cursor.fetchone()
        cursor.execute(f'INSERT INTO notas (tituloNota,conteNota,idUser) VALUES("{tituloNota}","{contenidoNota}","{idUser[0]}")')
        conexion.connection.commit ()
        return redirect(url_for('home'))

    return render_template('session/create.html')

@app.route('/update/<int:idnota>',methods=['POST','GET'])
def update(idnota):
    cursor = conexion.connection.cursor()
    if request.method == 'POST':
        tituloNota = request.form['tituloNota']
        contenidoNota = request.form['contenidoNota']    
        cursor.execute(f'UPDATE notas SET tituloNota = "{tituloNota}",conteNota ="{contenidoNota}" WHERE idnotas = {idnota} ')
        conexion.connection.commit ()
        return redirect(url_for('home'))
    cursor.execute(f'SELECT tituloNota,conteNota FROM notas WHERE idnotas = {idnota} ')
    campos = cursor.fetchone()
    return render_template('session/update.html',campos=campos,id=idnota)

@app.route('/delete/<int:idnota>',methods=['POST','GET'])
def delete(idnota):
    cursor = conexion.connection.cursor()
    cursor.execute(f'DELETE FROM notas WHERE idnotas={idnota}')
    conexion.connection.commit ()

    return redirect(url_for('home'))


@app.route('/logout')
def logout():
    session.pop('username')
    session.pop('email')
    
    return redirect(url_for('singin'))

if __name__ == '__main__':
    app.config.from_object(config['develop'])
    app.run()
