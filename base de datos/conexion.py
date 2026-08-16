import pymysql 

def obtener_conexion():
    return  pymysql.connect(
    host= "127.0.0.1",
    port=8889,
    user="root",
    password="root",
    database="Panama_Express",
    cursorclass=pymysql.cursors.DictCursor
)