import os

from re import T

from flask import flash
from flask_pinturas.config.mysqlconnection import connectToMySQL
from flask_pinturas.models import modelo_base
from flask_pinturas.models import pintura
from flask_pinturas.utils.regex import REGEX_CORREO_VALIDO

class Usuario(modelo_base.ModeloBase):

    #declaracion nombre de la tabla
    modelo = 'usuarios'
    #declaracion nombre los campos de la tabla
    campos = ['usuario', 'nombre','apellido','email','password']

    #declaracion del objeto
    def __init__(self, data):
        self.id = data['id']
        self.usuario = data['usuario']
        self.nombre = data['nombre']
        self.apellido = data['apellido']
        self.email = data['email']
        self.password = data['password']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        #en este campo se almacenaran una lista de objetos con las pinturas agregadas (pintadas) por el usuario
        self.pinturas = []
        #en este campo se almacenaran las pinturas a las que el usuario es comprador
        self.pinturas_compradores = []


    #metodo de clase para buscar el usuario para login
    @classmethod
    def buscar(cls, dato):
        query = "select * from usuarios where usuario = %(dato)s OR email = %(dato)s"
        data = { 'dato' : dato }

        results = connectToMySQL(os.environ.get("BASEDATOS_NOMBRE")).query_db(query, data)

        if len(results) < 1:
            return False

        return cls(results[0])

    #metodo de clase para actualizar un registro de usuario en la base de datos
    @classmethod
    def update(cls,data):
        query = """UPDATE usuarios
                        SET nombre = %(nombre)s,
                            apellido = %(apellido)s,
                            email = %(email)s,
                            usuario = %(usuario)s,
                        updated_at=NOW()
                    WHERE id = %(id)s"""
        resultado = connectToMySQL(os.environ.get("BASEDATOS_NOMBRE")).query_db(query, data)
        return resultado

    #metodo estatico para validar el largo de un campo de la tabla usuarios
    @staticmethod
    def validar_largo(data, campo, largo):
        is_valid = True
        if len(data[campo]) <= largo:
            flash(f'El largo del {campo} no puede ser menor o igual {largo}', 'error')
            is_valid = False
        return is_valid

    #metodo de clase para validar campos de la tabla usuarios
    @classmethod
    def validar(cls, data):

        is_valid = True
        #se crea una variable no_create para evitar la sobre escritura de la variable is_valid
        #pero a la vez se vean todos los errores al crear el usuario
        #y no tener que hacer un return por cada error
        no_create = is_valid


        is_valid = cls.validar_largo(data, 'usuario', 3)
        if is_valid == False: no_create = False
        is_valid = cls.validar_largo(data, 'nombre', 1)
        if is_valid == False: no_create = False
        is_valid = cls.validar_largo(data, 'apellido', 1)
        if is_valid == False: no_create = False
        is_valid = cls.validar_largo(data, 'password', 7)
        if is_valid == False: no_create = False


        if not REGEX_CORREO_VALIDO.match(data['email']):
            flash('El correo no es válido', 'error')
            is_valid = False

        if is_valid == False: no_create = False

        if data['password'] != data['cpassword']:
            flash('las contraseñas no son iguales', 'error')
            is_valid = False

        if is_valid == False: no_create = False

        if cls.validar_existe('usuario', data['usuario']):
            flash('el usuario ya esta ingresado', 'error')
            is_valid = False

        if is_valid == False: no_create = False

        if cls.validar_existe('email', data['email']):
            flash('el correo ya fue ingresado', 'error')
            is_valid = False

        if is_valid == False: no_create = False

        return no_create

    #metodo de clase para validar solo los campos de la actualizacion del usuario
    @classmethod
    def validar_update(cls, data):

        is_valid = True
        #se crea una variable no_create para evitar la sobre escritura de la variable is_valid
        #pero a la vez se vean todos los errores al crear el usuario
        #y no tener que hacer un return por cada error
        no_create = is_valid


        is_valid = cls.validar_largo(data, 'usuario', 3)
        if is_valid == False: no_create = False
        is_valid = cls.validar_largo(data, 'nombre', 1)
        if is_valid == False: no_create = False
        is_valid = cls.validar_largo(data, 'apellido', 1)
        if is_valid == False: no_create = False

        if not REGEX_CORREO_VALIDO.match(data['email']):
            flash('El correo no es válido', 'error')
            is_valid = False

        if is_valid == False: no_create = False


        return no_create




    #metodo de clase para validar la contrasena en el login
    @classmethod
    def validar_contrasena(cls,data):

        is_valid = cls.validar_largo(data, 'password', 7)

        no_update = is_valid

        if is_valid == False: no_update = False

        if data['password'] != data['cpassword']:
            flash('las contraseñas no son iguales', 'error')
            is_valid = False

        if is_valid == False: no_update = False

        return no_update



    #metodo que permite obtener las pinturas agregadas o poublicadas por un usuario
    #relacion de 1 a muchos = 1 usuario es pintordor o agrego muchas pinturas
    @classmethod
    def get_pinturas_de_usuario( cls , data ):
        #consulta join entre las tablas usuarios y pinturas
        query = "SELECT *, count(c.id_pintura) as count_compradores FROM usuarios u LEFT JOIN pinturas p ON u.id = p.id_pintor left join compradores c on p.id = c.id_pintura WHERE u.id = %(id)s group by p.id ;"
        results = connectToMySQL(os.environ.get("BASEDATOS_NOMBRE")).query_db( query , data )
        # los resultados serán una lista de objetos usuarios (users) que se adjunta a cada fila
        usuario = cls(results[0])

        #por medio de este ciclo se agrega en el  atributo pinturas del objeto usuario
        #las pinturas que agrego
        for row_from_db in results:
           # ahora parseamos los datos de pinturas para crear instancias de usuarios y agregarlas a nuestra lista
           pintura_data = {
               "id" : row_from_db["p.id"],
               "titulo" : row_from_db["titulo"],
               "descripcion" : row_from_db["descripcion"],
               "precio" : row_from_db["precio"],
               "cantidad" : row_from_db["cantidad"],
               "id_pintor" : row_from_db["id_pintor"],
               "nombre"   : row_from_db["nombre"],
               "apellido" : row_from_db["apellido"],
               "created_at": row_from_db["p.created_at"],
               "updated_at": row_from_db["p.updated_at"],
               "count_compradores" : row_from_db["count_compradores"],
           }

           #en la propiedad pinturas del objeto usuario se agregaran la lista de pinturas que tiene pintada (agregada) por cada usuario
           usuario.pinturas.append(pintura.Pintura( pintura_data ) )
        return usuario


    #parte 1 de relacion muchos a muchos = muchos usuarios son compradores de muchas pinturas
    @classmethod
    def get_pinturas_compradores_usuario( cls , data ):
 

        query = "SELECT * FROM usuarios u LEFT JOIN compradores c ON u.id = c.id_usuario LEFT JOIN pinturas p ON p.id = c.id_pintura left join usuarios u2 on p.id_pintor = u2.id   WHERE u.id = %(id)s;"

        results = connectToMySQL(os.environ.get("BASEDATOS_NOMBRE")).query_db( query , data )
        
        
        # los resultados serán una lista de objetos usuarios (users) que se adjunta a cada fila
        usuario = cls( results[0] )

        for row_from_db in results:
           # ahora parseamos las pinturas para crear instancias de pinturas y agregarlas a nuestra lista
           pintura_data = {
               "id" : row_from_db["p.id"],
               "titulo" : row_from_db["titulo"],
               "descripcion" : row_from_db["descripcion"],
               "precio" : row_from_db["precio"],
               "cantidad" : row_from_db["cantidad"],
               "id_pintor" : row_from_db["id_pintor"],
               "nombre" : row_from_db["u2.nombre"],
               "apellido" : row_from_db["u2.apellido"],
               "count_compradores" : 0,
               "created_at" : row_from_db["p.created_at"],
               "updated_at" : row_from_db["p.updated_at"]
           }
           #en la propiedad pinturas_compradores del objeto usuario se agregaran la lista de pinturas a las que el usuario es comprador
           usuario.pinturas_compradores.append( pintura.Pintura( pintura_data ) )

        return usuario

