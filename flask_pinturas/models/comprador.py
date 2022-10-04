import os
from re import T
from flask_pinturas.config.mysqlconnection import connectToMySQL
from flask_pinturas.models import modelo_base


class Comprador(modelo_base.ModeloBase):

    modelo = 'publicaciones'
    campos = ['id_usuario','id_pintura']

    def __init__(self, data):
        self.id_usuario = data['id_usuario']
        self.id_pintura = data['id_pintura']
        self.id_pintura = data['id_created_at']



    @classmethod
    def save(cls,data):
        query = "insert into compradores (id_usuario, id_pintura,created_at) values (%(id_usuario)s, %(id_pintura)s, now())"

        resultado = connectToMySQL(os.environ.get("BASEDATOS_NOMBRE")).query_db(query, data)
        return resultado


    @classmethod
    def delete(cls,data):
        query = """DELETE from compradores
                    WHERE id_usuario = %(id_usuario)s and id_pintura = %(id_pintura)s"""
        #print(query,flush=True)

        resultado = connectToMySQL(os.environ.get("BASEDATOS_NOMBRE")).query_db(query, data)
        return resultado

    #este metodo ejecuta el uno a muchos desde el lado de las pinturas
    @classmethod
    def get_all_compradores_usuarios(cls, data ):
        
        query = "SELECT * FROM pinturas p LEFT JOIN usuarios u on p.id_pintor = u.id left join compradores c ON p.id = c.id_pintura LEFT JOIN usuarios u2 ON u2.id = c.id_usuario WHERE p.id = %(id)s;"

        results = connectToMySQL(os.environ.get("BASEDATOS_NOMBRE")).query_db(query,data)
        all_data = []
        for data in results:
            all_data.append(data['id_usuario'])

        return all_data


