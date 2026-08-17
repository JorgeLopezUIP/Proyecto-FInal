import pymysql 

def obtener_conexion():
    return  pymysql.connect(
    host= "127.0.0.1",
    port=3307,
    user="root",
    password="root123",
    database="Panama_Express",
    cursorclass=pymysql.cursors.DictCursor
)