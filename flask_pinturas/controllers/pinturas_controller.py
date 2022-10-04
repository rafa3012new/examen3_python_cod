import os
from re import T
import re
from flask import redirect, render_template, request, flash, session
from flask_pinturas import app
from flask_pinturas.models.pintura import Pintura
from flask_pinturas.models.usuario import Usuario
from flask_pinturas.models.comprador import Comprador


#procedmiento que llama a la pagina para agregar Pintura
@app.route("/agregarpintura")
def agregar_pintura():
    return render_template('/agregar_pintura.html')

#procedmiento que llama a la pagina para agregar Pintura
@app.route("/editarpintura/<int:id>")
def editar_pintura(id):
    resulta = Pintura.get_by_id(id)
    return render_template('/editar_pintura.html',datoseditar=resulta)


#procedmiento que agrega una pintura al usuario
@app.route("/procesar_agregarpintura", methods=["POST"])
def procesar_agregar_pintura():

    if not Pintura.validar(request.form):
        return redirect('/')

    data = {
        'titulo': request.form['titulo'],
        'descripcion': request.form['descripcion'],
        'cantidad': request.form['cantidad'],
        'precio': request.form['precio'],
        'id_pintor': session['idusuario']
    }

    pintura = Pintura.save(data)

    if not pintura:
        flash("no se agregar la pintura","error")

    return redirect('/')


#procedmiento que agrega una pintura al usuario
@app.route("/procesar_editarpintura", methods=["POST"])
def procesar_editar_pintura():

    if not Pintura.validar(request.form):
        return redirect('/')

    data = {
        'titulo': request.form['titulo'],
        'descripcion': request.form['descripcion'],
        'cantidad': request.form['cantidad'],
        'precio': request.form['precio'],
        'id': request.form['id']
    }

    pintura = Pintura.update(data)
    

    return redirect('/')


#procedmiento que elimina la pintura agregada del usuario
@app.route("/eliminarpintura/<int:id>")
def eliminar_pintura(id):

    data = {
        'id':  id
    }

    resultado = Pintura.delete(data)


    return redirect('/')







#procedmiento que graba la compra de un usuario de una pintura
@app.route("/comprarpintura/<int:id_pintura>")
def comprar_pintura(id_pintura):

    data = {
        'id_usuario': session['idusuario'],
        'id_pintura': id_pintura
    }

    pintor= Comprador.save(data)


    if pintor is 0:
       flash("Se registro la compra a la pintura # " + str(id_pintura),"success")
    else:
       flash("Error al registrar la compras a la pintura no puede comprar doble ","error")

    return redirect('/')


#procedmiento que muestra los detalle de la pintura
@app.route("/verdetallepintura/<int:id>")
def ver_detalle_pintura(id):

    data = {
        'id':  id
    }

    resultado = Pintura.get_usuarios_compradores_pintura(data)

    return render_template("pintura.html", pintura_detalle = resultado)


