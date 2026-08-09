#Extract
import pandas as pd
from pathlib import Path
from conexion import *

script_dir = Path(__file__).resolve().parent
archivo = script_dir  / "manifiesto miami" / "manifiesto_miami_50_paquetes.xlsx"

df = pd.read_excel(archivo) #Lee el Excel para poder graficarlo en la consola

#print(df)

#Transform 
df["tracking"] = ( #Tabla de tracking
    df["tracking"]
    .astype(str) #Convierte los datos en string
    .str.strip() #Elimina los espacios en blanco
    .str.upper() #Pone el texto en mayusculas
    .str.replace("-", "", regex=False) #Elimina caracteres que sobran
)

df["cliente"] = ( #Tabla de clientes
    df["cliente"]
    .astype(str) #Convierte los datos en string
    .str.strip() #Elimina los espacios en blanco
)

df["descripcion"] = ( #Tabla de descripcion
    df["descripcion"]
    .astype(str) #Convierte los datos en string
    .str.strip() #Elimina los espacios en blanco
)

#Tabla peso
df["peso"] = pd.to_numeric(df["peso"], errors="coerce") #Convierte los datos en numeros

df_invalidos = df[df["peso"].isna() | (df["peso"] <= 0)].copy() #Detecta pesos no validos como datos N/A y menores a 0
df_validos = df[df["peso"].notna() & (df["peso"] > 0)].copy() #Detecta los pesos validos

duplicados = df_validos[
    df_validos.duplicated(
        subset = ["tracking"],
        keep=False
    )
]

df_validos = df_validos.drop_duplicates(
    subset=["tracking"],
    keep="first"
)

def clasificar_producto(descripcion): 
    descripcion = descripcion.lower()

    if any(palabra in descripcion for palabra in [
        "laptop", "tablet", "monitor", "televisor",
        "consola", "impresora", "cámara", "camara"
    ]): 
        return "Electronico"

    elif any(palabra in descripcion for palabra in [
        "camisa", "vestido", "pantalón", "pantalon",
        "blusa"
    ]):
        return "Ropa"

    elif "zapato" in descripcion:
        return "Calzado"

    elif any(palabra in descripcion for palabra in [
        "mouse", "teclado", "audífono", "audifono",
        "smartwatch"
    ]):
        return "Accesorios"

    else:
        return "Otros"

df_validos["categoria"] = df_validos["descripcion"].apply(clasificar_producto)

def calcular_tarifa(peso):
    if peso <= 1:
        return 5.00
    elif peso <= 5:
        return 8.00
    elif peso <= 10:
        return 12.00
    else:
        return 15.00

df_validos["tarifa_preliminar"] = df_validos["peso"].apply(calcular_tarifa)

print(df_validos)

print("Cantidad original:", len(df))
print("Registros inválidos:", len(df_invalidos))
print("Registros válidos:", len(df_validos))

#Load
conexion = obtener_conexion()
cursor = conexion.cursor()

def insertar_paquete(
    cursor,
    id_cliente,
    id_bodega,
    id_categoria_producto,
    nombre,
    tracking,
    peso,
    largo,
    ancho,
    alto,
    descripcion
):

    sql = """
        INSERT INTO paquetes (
            id_cliente,
            id_bodega,
            id_categoria_producto,
            nombre,
            tracking,
            peso,
            largo,
            ancho,
            alto,
            descripcion
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    cursor.execute(
        sql,
        (
            id_cliente,
            id_bodega,
            id_categoria_producto,
            nombre,
            tracking,
            peso,
            largo,
            ancho,
            alto,
            descripcion
        )
    )

def obtener_o_crear_categoria(cursor, nombre_categoria):

    sql = """
        SELECT id
        FROM categoria_productos
        WHERE nombre = %s
    """

    cursor.execute(sql, (nombre_categoria,))
    resultado = cursor.fetchone()

    if resultado:
        return resultado["id"]

    sql_insert = """
        INSERT INTO categoria_productos (
            nombre,
            descripcion
        )
        VALUES (%s, %s)
    """

    cursor.execute(
        sql_insert,
        (
            nombre_categoria,
            f"Categoría {nombre_categoria}"
        )
    )

    return cursor.lastrowid

def obtener_cliente(cursor, nombre_cliente):

    sql = """
        SELECT id
        FROM clientes
        WHERE nombre = %s
    """

    cursor.execute(sql, (nombre_cliente,))
    resultado = cursor.fetchone()

    if resultado:
        return resultado["id"]

    return None

def obtener_bodega(cursor, nombre_bodega):

    sql = """
        SELECT id
        FROM bodegas
        WHERE nombre = %s
    """

    cursor.execute(sql, (nombre_bodega,))
    resultado = cursor.fetchone()

    if resultado:
        return resultado["id"]

    return None

def paquete_existe(cursor, tracking):

    sql = """
        SELECT id
        FROM paquetes
        WHERE tracking = %s
    """

    cursor.execute(sql, (tracking,))

    return cursor.fetchone() is not None


insertados = 0
omitidos = 0
errores = 0

# Buscar automáticamente la bodega
id_bodega = obtener_bodega(
    cursor,
    "Bodega Miami"
)

if id_bodega is None:
    raise Exception("No se encontró la Bodega Miami")


for _, fila in df_validos.iterrows():

    try:

        tracking = fila["tracking"]
        nombre_cliente = fila["cliente"]
        peso = fila["peso"]
        descripcion = fila["descripcion"]
        categoria = fila["categoria"]


        if paquete_existe(cursor, tracking):

            print(
                f"{tracking} → ya existe, se omite"
            )

            omitidos += 1
            continue


        id_cliente = obtener_cliente(
            cursor,
            nombre_cliente
        )

        if id_cliente is None:

            print(
                f"{tracking} → cliente no encontrado: "
                f"{nombre_cliente}"
            )

            errores += 1
            continue


        id_categoria_producto = obtener_o_crear_categoria(
            cursor,
            categoria
        )

        insertar_paquete(
            cursor,
            id_cliente,
            id_bodega,
            id_categoria_producto,
            descripcion,
            tracking,
            peso,
            fila.get("largo"),
            fila.get("ancho"),
            fila.get("alto"),
            descripcion
        )

        insertados += 1

        print(
            f"{tracking} → insertado correctamente"
        )


    except Exception as e:

        print(
            f"{fila['tracking']} → ERROR: {e}"
        )

        errores += 1



conexion.commit()


print()
print("==============================")
print("       RESULTADO DEL ETL")
print("==============================")
print(f"Insertados : {insertados}")
print(f"Omitidos   : {omitidos}")
print(f"Errores    : {errores}")
print("==============================")

