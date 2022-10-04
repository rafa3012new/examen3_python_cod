import os
from re import T

from flask import flash
from flask_pinturas.config.mysqlconnection import connectToMySQL
from flask_pinturas.models import modelo_base
from flask_pinturas.models import usuario
from flask_pinturas.models import comprador
from flask_pinturas.utils.regex import REGEX_CORREO_VALIDO


class Pintura(modelo_base.ModeloBase):

    modelo = 'pinturas'
    campos = ['titulo','descripcion','id_pintor', 'cantidad', 'precio']

    def __init__(self, data):
        self.id = data['id']
        self.titulo = data['titulo']
        self.descripcion = data['descripcion']
        self.id_pintor = data['id_pintor']
        self.cantidad = data['cantidad']
        self.precio = data['precio']
        self.id_pintor = data['id_pintor']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.nombre_usuario = data['nombre']
        self.apellido_usuario = data['apellido']
        self.count_compradores = data['count_compradores']
        self.usuarios_compradores = []



    #(nadie mas puede pintar el mismo titulo de tu pintura) pendiente
    @classmethod
    def save(cls,data):
        query = "insert into pinturas (titulo, descripcion, id_pintor, cantidad, precio, created_at, updated_at) values (%(titulo)s, %(descripcion)s,  %(id_pintor)s, %(cantidad)s, %(precio)s, NOW(), NOW())"

        resultado = connectToMySQL(os.environ.get("BASEDATOS_NOMBRE")).query_db(query, data)
        return resultado

    #opcional
    @classmethod
    def update(cls,data):
        query = "UPDATE pinturas SET titulo = %(titulo)s, descripcion = %(descripcion)s, cantidad = %(cantidad)s,precio = %(precio)s, updated_at = NOW() WHERE id = %(id)s;"
        resultado = connectToMySQL(os.environ.get("BASEDATOS_NOMBRE")).query_db(query, data)

        return resultado

    @classmethod
    def delete(cls,data):
        query = """DELETE from pinturas
                    WHERE id = %(id)s"""

        resultado = connectToMySQL(os.environ.get("BASEDATOS_NOMBRE")).query_db(query, data)
        return resultado


    #este metodo ejecuta una consulta de el uno a muchos desde el lado de las pinturas mas sus compradores
    @classmethod
    def get_all_join_usuarios(cls):

        query = f"SELECT *, count(c.id_pintura) as count_compradores FROM pinturas p left join usuarios u on p.id_pintor = u.id left join compradores c on p.id = c.id_pintura group by p.id;"

        results = connectToMySQL(os.environ.get("BASEDATOS_NOMBRE")).query_db(query)

        all_data = []
        for data in results:
            data2 = {'id':data['id']}
            lista = comprador.Comprador.get_all_compradores_usuarios(data2)
            objeto = cls(data)
            # se asigna directamente sin append  el campo arreglo usuarios_compradores
            # del objeto que con este metodo tendra el contenido obtenido en lista
            objeto.usuarios_compradores = lista
            all_data.append(objeto)
        return all_data


    @classmethod
    def get_usuarios_compradores_pintura( cls , data ):
        
        query = "SELECT *, 0 as count_compradores FROM pinturas p LEFT JOIN usuarios u on p.id_pintor = u.id left join compradores c ON p.id = c.id_pintura LEFT JOIN usuarios u2 ON u2.id = c.id_usuario WHERE p.id = %(id)s;"


        results = connectToMySQL(os.environ.get("BASEDATOS_NOMBRE")).query_db( query , data )
        # los resultados serán una lista de objetos usuarios (users) que se adjunta a cada fila
        pintura = cls(results[0])

        #reinicio  el campo arreglo usuarios_compradores del objeto que
        # con este metodo tendra el contenido a continuacion
        pintura.usuarios_compradores = []
 
        count_compradores = 0
        #se obtiene el detalle de los compradores de la pintura
        for row_from_db in results:
           if row_from_db["id_usuario"] != None:
             count_compradores+=1
           # ahora parseamos los datos usuarios para crear instancias de usuarios y agregarlas a nuestra lista
           usuario_data = {
               "id" : row_from_db["u2.id"],
               "usuario" : row_from_db["u2.usuario"],
               "password" : row_from_db["u2.password"],
               "nombre" : row_from_db["u2.nombre"],
               "apellido" : row_from_db["u2.apellido"],
               "email" : row_from_db["u2.email"],
               "created_at" : row_from_db["u2.created_at"],
               "updated_at" : row_from_db["u2.updated_at"]
           }
           pintura.usuarios_compradores.append( usuario.Usuario( usuario_data ) )

        #se obtiene el numero de compradores de la pintura
        pintura.count_compradores=count_compradores

        return pintura



    @staticmethod
    def validar_largo(data, campo, largo):
        is_valid = True
        if len(data[campo]) <= largo:
            flash(f'El largo del {campo} no puede ser menor o igual {largo}', 'error')
            is_valid = False
        return is_valid

    @staticmethod

    def validar_cantidad_mayor(data, campo, valor):
        is_valid = True
        if float(data[campo]) <= valor:
            flash(f'El valor de {campo} no puede ser menor o igual {valor}', 'error')
            is_valid = False
        return is_valid



    @classmethod
    def validar(cls, data):

        is_valid = True
        #se crea una variable no_create para evitar la sobre escritura de la variable is_valid
        #pero a la vez se vean todos los errores al crear el usuario
        #y no tener que hacer un return por cada error
        no_create = is_valid


        is_valid = cls.validar_largo(data, 'titulo', 3)

        if is_valid == False: no_create = False

        is_valid = cls.validar_largo(data, 'descripcion', 11)

        if is_valid == False: no_create = False


        is_valid = cls.validar_cantidad_mayor(data, 'cantidad', 0)

        if is_valid == False: no_create = False

        is_valid = cls.validar_cantidad_mayor(data, 'precio', 0)

        if is_valid == False: no_create = False


        if is_valid == False: no_create = False


        return no_create

