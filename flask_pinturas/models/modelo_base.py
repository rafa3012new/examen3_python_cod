import os

from flask_pinturas.config.mysqlconnection import connectToMySQL

class ModeloBase():

    # modelo = '' indicar modelo
    # campos = [] aca indicar todos los campos del hijo

    #metodo de clase que valida que un registro existe para cualquier tabla
    @classmethod
    def validar_existe(cls, campo, valor):
        query = f"SELECT count(*) as contador FROM {cls.modelo} WHERE {campo} = %({campo})s;"
        data = { campo : valor }
        results = connectToMySQL(os.environ.get("BASEDATOS_NOMBRE")).query_db(query, data)
        return results[0]['contador'] > 0

    #metodo de clase que obtiene todos los registros de cualquier tabla
    #y los devuelve como objetos
    @classmethod
    def get_all(cls):
        query = f"SELECT * FROM {cls.modelo};"
        results = connectToMySQL(os.environ.get("BASEDATOS_NOMBRE")).query_db(query)
        all_data = []
        for data in results:
            all_data.append(cls(data))
        return all_data


    #metodo de clase que devuelve un registro por id para cualquier tabla
    @classmethod
    def get_by_id(cls, id):
        query = f"SELECT * FROM {cls.modelo} WHERE id = %(id)s"
        data = { 'id' : id }
        results = connectToMySQL(os.environ.get("BASEDATOS_NOMBRE")).query_db(query, data)
        return results


    #metodo de clase que elimina un registro para cualquier tabla
    @classmethod
    def delete(cls,id):
        query = f"DELETE FROM {cls.modelo} WHERE id = %(id)s"
        data = {
            'id': id
        }
        resultado = connectToMySQL(os.environ.get("BASEDATOS_NOMBRE")).query_db(query, data)
        print("RESULTADO: ", resultado)
        return resultado

    #metodo de clase que graba un registro para cualquier tabla
    @classmethod
    def save(cls, data):

        campos_header = ''
        campos_datos = ''
        for campo in cls.campos:
            campos_header += campo + ','
            campos_datos += f'%({campo})s,'

        query = f"""
                INSERT INTO {cls.modelo} ({campos_header}created_at, updated_at)
                VALUES ({campos_datos} NOW(), NOW());
                """
        print(query,flush=True)
        print("ver depues de insert",flush=True)
        resultado = connectToMySQL(os.environ.get("BASEDATOS_NOMBRE")).query_db(query, data)
        print("RESULTADO: ", resultado)
        return resultado