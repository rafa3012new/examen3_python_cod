import os
from re import T
import re
from flask import redirect, render_template, request, flash, session
from flask_pinturas import app
from flask_pinturas.models.pintura import Pintura
from flask_pinturas.models.usuario import Usuario
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt(app)


#ruta inicial
@app.route("/")
def index():

    #si el usuario no se encuentra logeao genera error y devuelve al login
    if 'usuario' not in session:
        flash('Primero debe logearse', 'error')
        return redirect('/login')

    #se obtienen los datos de las pinturas pitadas por todos los usuarios
    # para se borradas o modificadas solo las del usuario de la sesion
    pinturas = Pintura.get_all_join_usuarios()

    #se obtienen los datos de las pinturas compradas por el usuario
    # que inicio la sesion
    data = {'id':session['idusuario']}

    compras_usuario = Usuario.get_pinturas_compradores_usuario(data)
 
    #se setea en una variable el nombre del sistema
    nombre_sistema = os.environ.get("NOMBRE_SISTEMA")
    
    #se rederiza la  pagina principal y se le envia la data de las consultas
    return render_template("index.html", sistema=nombre_sistema, lista_pinturas = pinturas, lista_compras_usuario=compras_usuario)



#ruta del login
@app.route("/login")
def login():

    if 'usuario' in session:
        flash('Ud ya está LOGEADO!', 'warning')
        return redirect('/')

    return render_template("login.html")


# se procesa el registro del usuario
@app.route("/procesar_registro", methods=["POST"])
def procesar_registro():

    if not Usuario.validar(request.form):
        return redirect('/login')

    pass_hash = bcrypt.generate_password_hash(request.form['password'])

    data = {
        'usuario' : request.form['usuario'],
        'nombre' : request.form['nombre'],
        'apellido' : request.form['apellido'],
        'email' : request.form['email'],
        'password' : pass_hash,
    }


    resultado = Usuario.save(data)

    if not resultado:
        flash("Error al crear el usuario", "error")
        return redirect("/login")

    flash("Usuario creado correctamente", "success")
    return redirect("/login")




#se procesa el acceso de login
@app.route("/procesar_login", methods=["POST"])
def procesar_login():

    usuario = Usuario.buscar(request.form['identificacion'])

    if not usuario:
        flash("Usuario/Correo/Clave Invalidas", "error")
        return redirect("/login")

    if not bcrypt.check_password_hash(usuario.password, request.form['password']):
        flash("Usuario/Correo/Clave Invalidas", "error")
        return redirect("/login")


    session['idusuario'] = usuario.id
    session['usuario'] = usuario.nombre

    return redirect('/')






#se cierra el login
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')



