import pandas as pd
from conexion import obtener_conexion


def obtener_cliente(cursor, cedula): #Busca al cliente en la base de datos segun su cedula

    sql = """
        SELECT id
        FROM clientes
        WHERE cedula_pasaporte = %s
    """

    cursor.execute(
        sql,
        (cedula,)
    )

    resultado = cursor.fetchone()

    if resultado:
        return resultado["id"]

    return None


def obtener_bodega(cursor, nombre_bodega): #Selecciona una bodega en la base de datos segun su nombre

    sql = """
        SELECT id
        FROM bodegas
        WHERE nombre = %s
    """

    cursor.execute(
        sql,
        (nombre_bodega,)
    )

    resultado = cursor.fetchone()

    if resultado:
        return resultado["id"]

    return None


def obtener_o_crear_categoria( #Busca la categoria segun el producto
    cursor,
    nombre_categoria
):

    sql = """
        SELECT id
        FROM categoria_productos
        WHERE nombre = %s
    """

    cursor.execute(
        sql,
        (nombre_categoria,)
    )

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


def paquete_existe(cursor, tracking): #Verifica si el paquete existe en la base de datos, si existe lo omite

    sql = """
        SELECT id
        FROM paquetes
        WHERE tracking = %s
    """

    cursor.execute(
        sql,
        (tracking,)
    )

    return cursor.fetchone() is not None



#Load
def cargar_datos(archivo):

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:

        df = pd.read_csv(archivo) #Lee el archivo CSV que contiene los datos transformados

        insertados = 0
        omitidos = 0
        errores = 0

        #Guardar el mensaje de cada registro procesado en una lista para mostrarlo en la interfaz web

        mensajes = []


        
        #Todos los paquetes iran a la Bodega Miami
        id_bodega = obtener_bodega(
            cursor,
            "Bodega Miami"
        )

        #Si no se encuentra la bodega se lanza una excepción que detiene el proceso
        if id_bodega is None:

            raise Exception(
                "No se encontró la Bodega Miami."
            )


        for _, fila in df.iterrows(): #Procesa cada fila del Dataframe

            tracking = fila["tracking"] #Se guarda el tracking de los paquetes para detectar duplicados


            try:
                #Se guardan los datos de la tabla en variables
                cedula = fila["cedula"]
                peso = fila["peso"]
                descripcion = fila["descripcion"]
                categoria = fila["categoria"]


                
                #Comprobrar si el paquete ya existe en la base de datos, si existe se omite el registro
                if paquete_existe(
                    cursor,
                    tracking
                ):

                    omitidos += 1 #Se suma un omitido si sucede esto

                    mensajes.append(
                        f"{tracking} → "
                        f"OMITIDO: el tracking ya existe en la base de datos."
                    )

                    #No se continua con el resto del registro para este paquete, se pasa al siguiente

                    continue


               
                #El cliente se busca mediante su cedula, no su nombre
                id_cliente = obtener_cliente(
                    cursor,
                    cedula
                )

                #Si la cedula no corresponde a ningun cliente se omite el registro del paquete
                if id_cliente is None:

                    errores += 1 #Se suma un error si sucede esto

                    mensajes.append(
                        f"{tracking} → "
                        f"ERROR: no se encontró un cliente "
                        f"con la cédula {cedula}."
                    )

                    continue


                
                #Obtiene el id de la categoria del producto, si no existe la crea
                id_categoria = (
                    obtener_o_crear_categoria(
                        cursor,
                        categoria
                    )
                )


                
                #Se inserta el paquere, relacionando el cliente, la bodega y la categoria del producto segun su ID
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
                    VALUES (
                        %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s
                    )
                """


                cursor.execute(
                    sql,
                    (
                        id_cliente,
                        id_bodega,
                        id_categoria,
                        descripcion,
                        tracking,
                        peso,
                        fila.get("largo (cm)"),
                        fila.get("ancho (cm)"),
                        fila.get("altura (cm)"),
                        descripcion
                    )
                )


                insertados += 1 #Se suma un insertado si el paquete se inserta correctamente

                #Se guarda un mensaje de éxito para mostrarlo en la interfaz web
                mensajes.append(
                    f"{tracking} → "
                    f"INSERTADO: paquete cargado correctamente."
                )

            #Si un registro produce un error no se detiene todo el proceso
            except Exception as e:

                errores += 1

                mensajes.append(
                    f"{tracking} → "
                    f"ERROR: {e}"
                )


        conexion.commit() #Confirmar los cambios en la base de datos

        #Se devuelve un diccionario con el resumen de la carga de datos para mostrarlo en la interfaz web
        return {

            "insertados": insertados,

            "omitidos": omitidos,

            "errores": errores,

            "mensajes": mensajes

        }

    #Deshace los cambios si ocurre un error durante la carga de datos
    except Exception:

        conexion.rollback()

        raise


    finally:

        cursor.close()
        conexion.close()