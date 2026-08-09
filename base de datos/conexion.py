import pymysql 


conexion = pymysql.connect(
    host= "localhost",
    port=3307,
    user="user",
    password="pass123",
    database="Panama_Express",
    cursorclass=pymysql.cursors.DictCursor
)


def obtener_conexion():
    return conexion