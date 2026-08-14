import pandas as pd
import pymysql
from conexion import obtener_conexion


METODOS_VALIDOS = {"aereo", "maritimo", "terrestre"}


def _cargar_referencias(cursor):
    """Precarga clientes, categorias y bodega para no consultar la BD fila por fila."""

    cursor.execute("SELECT id, cedula_pasaporte FROM clientes")
    clientes = {row["cedula_pasaporte"]: row["id"] for row in cursor.fetchall()}

    cursor.execute("SELECT id, nombre FROM categoria_productos")
    categorias = {row["nombre"]: row["id"] for row in cursor.fetchall()}

    # No hay bodega en el CSV del ETL, asi que se usa la primera bodega
    # registrada como destino por defecto.
    cursor.execute("SELECT id FROM bodegas LIMIT 1")
    fila_bodega = cursor.fetchone()
    id_bodega = fila_bodega["id"] if fila_bodega else None

    return clientes, categorias, id_bodega


def cargar_datos(archivo_csv):
    df = pd.read_csv(archivo_csv, encoding="utf-8-sig")

    insertados = 0
    omitidos = 0
    errores = 0
    mensajes = []

    conexion = obtener_conexion()

    try:
        with conexion.cursor() as cursor:

            clientes, categorias, id_bodega = _cargar_referencias(cursor)

            if id_bodega is None:
                return {
                    "insertados": 0,
                    "omitidos": 0,
                    "errores": len(df),
                    "mensajes": [
                        "ERROR: no hay ninguna bodega registrada en la base de datos"
                    ],
                }

            for _, fila in df.iterrows():
                tracking = fila["tracking"]

                try:
                    # Cliente: el paquete solo puede insertarse si ya existe
                    # un cliente con esa cedula (paquetes.id_cliente es FK).
                    id_cliente = clientes.get(fila["cedula"])
                    if id_cliente is None:
                        omitidos += 1
                        mensajes.append(
                            f"OMITIDO {tracking}: cliente con cedula "
                            f"{fila['cedula']} no esta registrado"
                        )
                        continue

                    # Categoria: mapea 1 a 1 con lo que devuelve
                    # clasificar_producto() en Transform_flask.py.
                    id_categoria = categorias.get(fila["categoria"])
                    if id_categoria is None:
                        omitidos += 1
                        mensajes.append(
                            f"OMITIDO {tracking}: categoria "
                            f"'{fila['categoria']}' no existe en el catalogo"
                        )
                        continue

                    # metodo_de_llegada es ENUM en minusculas; Transform_flask
                    # lo deja en mayusculas, asi que se normaliza aqui.
                    metodo = str(fila.get("metodo de llegada", "")).strip().lower()
                    if metodo not in METODOS_VALIDOS:
                        omitidos += 1
                        mensajes.append(
                            f"OMITIDO {tracking}: metodo de llegada "
                            f"'{metodo}' no es valido"
                        )
                        continue

                    cursor.execute(
                        """
                        INSERT INTO paquetes (
                            id_cliente, id_bodega, id_categoria_producto,
                            nombre, tracking, peso, descripcion, metodo_de_llegada
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                        (
                            id_cliente,
                            id_bodega,
                            id_categoria,
                            fila["descripcion"],   # no hay columna "nombre" separada en el CSV
                            tracking,
                            fila["peso"],
                            fila["descripcion"],
                            metodo,
                        )
                    )

                    id_paquete = cursor.lastrowid

                    # Primer evento del historial de tracking del paquete.
                    cursor.execute(
                        """
                        INSERT INTO tracking_eventos (id_paquete, estado, comentario)
                        VALUES (%s, %s, %s)
                        """,
                        (id_paquete, "recibido en bodega", "Ingreso automatico via ETL")
                    )

                    # Se confirma fila por fila: si la siguiente falla, no
                    # arrastra un rollback sobre lo que ya se insertó bien.
                    conexion.commit()

                    insertados += 1
                    mensajes.append(f"OK  {tracking} \u00b7 {fila['cliente']} insertado")

                except pymysql.err.IntegrityError:
                    # tracking (u otra columna UNIQUE) ya existe.
                    omitidos += 1
                    mensajes.append(f"OMITIDO {tracking}: ya existe en la base de datos")
                    conexion.rollback()

                except Exception as e:
                    errores += 1
                    mensajes.append(f"ERROR {tracking}: {e}")
                    conexion.rollback()

    finally:
        conexion.close()

    return {
        "insertados": insertados,
        "omitidos": omitidos,
        "errores": errores,
        "mensajes": mensajes,
    }
