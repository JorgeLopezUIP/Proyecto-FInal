from flask import Flask, render_template, request, session, jsonify
import pandas as pd
import os
import uuid
from datetime import datetime

try:
    from dotenv import load_dotenv
    load_dotenv()  # lee .env si existe; si no existe, no hace nada
except ImportError:
    pass  # python-dotenv es opcional -- sin el, exporta las variables a mano

from Transform_flask import transformar_datos
from Load_flask import cargar_datos
from Random_flask import generar_paquetes_aleatorios
from conexion import obtener_conexion
from correo import notificar_cambio_estado


app = Flask(__name__)

# En producción, define SECRET_KEY como variable de entorno.
app.secret_key = os.environ.get("SECRET_KEY", "clave-secreta")

ESTADOS_VALIDOS = {
    "recibido en bodega", "en transito", "en aduana", "listo para retiro"
}
METODOS_VALIDOS = {"aereo", "maritimo", "terrestre"}


def error_page(codigo, titulo, mensaje, stage_hint="extract"):
    return render_template(
        "error.html",
        codigo=codigo,
        titulo=titulo,
        mensaje=mensaje,
        stage_hint=stage_hint,
    )


# Inicio
@app.route("/")  # Ruta donde el usuario selecciona el archivo Excel para iniciar el proceso ETL
def index():
    session.clear()
    return render_template("index.html")


# Extract
@app.route("/extract", methods=["POST"])
def extract():

    archivo = request.files.get("archivo")

    if not archivo or archivo.filename == "":
        return error_page(
            "SIN ARCHIVO",
            "Ningún archivo seleccionado",
            "Vuelve al inicio y selecciona un archivo .xlsx antes de continuar.",
        )

    try:

        os.makedirs("datos", exist_ok=True)

        ruta = "datos/archivo_original.xlsx"

        archivo.save(ruta)

        df = pd.read_excel(ruta)

        # Se guarda la ruta del archivo Excel original para poder leerlo en TRANSFORM
        session["archivo_original"] = ruta
        session["archivo_nombre"] = archivo.filename
        session["lote"] = datetime.now().strftime("%y%m%d") + "-" + uuid.uuid4().hex[:4].upper()

        return render_template(
            "extract.html",
            total=len(df),
            tabla=df.to_html(
                classes="data-table",
                index=False
            )
        )

    except Exception as e:
        return error_page(
            "EXTRACT",
            "Error durante Extract",
            f"No se pudo leer el archivo: {e}",
        )


# Generar datos de prueba (alimenta el flujo de Extract con datos aleatorios)
@app.route("/generar", methods=["POST"])
def generar():

    try:
        cantidad = int(request.form.get("cantidad", 20))
    except (TypeError, ValueError):
        cantidad = 20
    cantidad = max(5, min(cantidad, 500))  # limites razonables

    try:
        os.makedirs("datos", exist_ok=True)

        df_generado = generar_paquetes_aleatorios(cantidad=cantidad)

        ruta = "datos/archivo_original.xlsx"
        df_generado.to_excel(ruta, index=False)

        df = pd.read_excel(ruta)

        session["archivo_original"] = ruta
        session["archivo_nombre"] = f"datos_generados_{cantidad}.xlsx"
        session["lote"] = datetime.now().strftime("%y%m%d") + "-" + uuid.uuid4().hex[:4].upper()

        return render_template(
            "extract.html",
            total=len(df),
            tabla=df.to_html(
                classes="data-table",
                index=False
            )
        )

    except Exception as e:
        return error_page(
            "GENERAR",
            "Error al generar datos de prueba",
            f"No se pudieron generar los datos: {e}",
        )


# Transform
def _ejecutar_transform(df):
    """Corre transformar_datos() sobre `df`, guarda el CSV de válidos para
    LOAD y arma la respuesta que consume transform.html. Se usa tanto desde
    /transform (primera corrida) como desde /transform/corregir (después de
    que el usuario edita filas inválidas y pide revalidar).

    Tambien guarda un "archivo de trabajo" con el DataFrame COMPLETO
    (validos + invalidos, ya con las correcciones aplicadas hasta ahora).
    Esto es clave para que las correcciones se acumulen entre rondas: si no
    se guardara, cada ronda de /transform/corregir tendria que releer el
    excel original sin tocar, y las filas corregidas en una ronda anterior
    (que ya no vienen en el formulario de la ronda actual, porque pasaron a
    validos) se sobrescribirian de vuelta con sus valores sucios originales."""

    resultado = transformar_datos(df)

    df_validos = resultado["validos"]
    df_invalidos = resultado["invalidos"]

    archivo_validos = os.path.abspath("datos/Datos_validos.csv")
    df_validos.to_csv(archivo_validos, index=False, encoding="utf-8-sig")
    session["archivo_validos"] = archivo_validos

    # `df` ya viene mutado en el lugar por transformar_datos() (le agrega
    # cedula_valida, limpia tracking/cedula/etc), y conserva TODAS las filas
    # en su orden original -- por eso sirve para reconstruir el estado
    # acumulado entre rondas de correccion.
    archivo_trabajo = os.path.abspath("datos/archivo_trabajo.csv")
    df.drop(columns=["cedula_valida"], errors="ignore").to_csv(
        archivo_trabajo, index=False, encoding="utf-8-sig"
    )
    session["archivo_trabajo"] = archivo_trabajo

    # Los invalidos se arman como lista de registros (no HTML fijo) para
    # poder mostrarlos como formulario editable en la plantilla, con el
    # indice original de fila (idx) para poder ubicarlos al corregir.
    invalidos_registros = []
    for idx, fila in df_invalidos.iterrows():
        invalidos_registros.append({
            "idx": int(idx),
            "tracking": fila["tracking"],
            "cedula": fila["cedula"],
            "cliente": fila["cliente"],
            "descripcion": fila["descripcion"],
            "peso": "" if pd.isna(fila["peso"]) else fila["peso"],
            "largo": "" if pd.isna(fila["largo"]) else fila["largo"],
            "ancho": "" if pd.isna(fila["ancho"]) else fila["ancho"],
            "alto": "" if pd.isna(fila["alto"]) else fila["alto"],
            "metodo": fila["metodo de llegada"],
            "motivo": fila["motivo"],
        })

    return render_template(
        "transform.html",
        total=len(df),
        validos=len(df_validos),
        invalidos=len(df_invalidos),
        duplicados=resultado["duplicados"],
        cedulas_invalidas=resultado["cedulas_invalidas"],
        pesos_invalidos=resultado["pesos_invalidos"],
        dimensiones_invalidas=resultado["dimensiones_invalidas"],
        tabla_validos=df_validos.to_html(classes="tabla", index=False),
        invalidos_registros=invalidos_registros,
    )


@app.route("/transform", methods=["POST"])
def transform():

    # Recuperamos la ruta del archivo Excel guardada en la sesión
    archivo = session.get("archivo_original")

    if not archivo or not os.path.exists(archivo):
        return error_page(
            "SIN EXTRACT",
            "No hay ningún archivo extraído",
            "Primero debes realizar Extract antes de continuar con Transform.",
        )

    try:
        # Pandas transforma el Excel en un DataFrame para poder manipularlo y graficarlo en la consola
        # Esta es siempre la primera corrida (viene de Extract), asi que se
        # parte del excel original -- cualquier archivo de trabajo de un
        # lote anterior ya no aplica (se pisa al llamar _ejecutar_transform).
        df = pd.read_excel(archivo)
        return _ejecutar_transform(df)

    except Exception as e:
        return error_page(
            "TRANSFORM",
            "Error durante Transform",
            f"No se pudieron validar los datos: {e}",
            stage_hint="transform",
        )


@app.route("/transform/corregir", methods=["POST"])
def transform_corregir():
    """Recibe las filas invalidas editadas desde la GUI y las aplica sobre
    el archivo de TRABAJO (no sobre el excel original), para que las
    correcciones de rondas anteriores no se pierdan. Luego vuelve a correr
    todo el Transform sobre el conjunto completo (asi los duplicados,
    categorias, etc. se recalculan bien)."""

    archivo_trabajo = session.get("archivo_trabajo")
    archivo_original = session.get("archivo_original")

    try:
        if archivo_trabajo and os.path.exists(archivo_trabajo):
            # Ya hay una ronda de correcciones previa: seguimos sobre eso.
            df = pd.read_csv(archivo_trabajo, encoding="utf-8-sig")
        elif archivo_original and os.path.exists(archivo_original):
            # Primera vez que se corrige: todavia no existe archivo de
            # trabajo, partimos del excel original.
            df = pd.read_excel(archivo_original)
        else:
            return error_page(
                "SIN EXTRACT",
                "No hay ningún archivo extraído",
                "Primero debes realizar Extract antes de continuar con Transform.",
            )

        # Estandarizamos nombres de columna igual que transformar_datos()
        # (no-op si ya vienen estandarizadas, como al leer el csv de trabajo).
        df.columns = (
            df.columns.astype(str).str.strip().str.lower().str.replace("-", "", regex=False)
        )

        # Se pasan a tipo object antes de editar: si una columna quedo tipada
        # como float64, pandas rechaza asignarle un string (ej. "5.0" o un
        # valor invalido a proposito como "N/A") con .at[].
        df["peso"] = df["peso"].astype(object)
        df["largo"] = df["largo"].astype(object)
        df["ancho"] = df["ancho"].astype(object)
        df["alto"] = df["alto"].astype(object)

        idxs = request.form.getlist("idx")
        trackings = request.form.getlist("tracking")
        cedulas = request.form.getlist("cedula")
        clientes = request.form.getlist("cliente")
        descripciones = request.form.getlist("descripcion")
        pesos = request.form.getlist("peso")
        largos = request.form.getlist("largo")
        anchos = request.form.getlist("ancho")
        altos = request.form.getlist("alto")
        metodos = request.form.getlist("metodo")

        for i, idx_str in enumerate(idxs):
            try:
                idx = int(idx_str)
            except ValueError:
                continue
            if idx not in df.index:
                continue
            df.at[idx, "tracking"] = trackings[i]
            df.at[idx, "cedula"] = cedulas[i]
            df.at[idx, "cliente"] = clientes[i]
            df.at[idx, "descripcion"] = descripciones[i]
            df.at[idx, "peso"] = pesos[i]
            df.at[idx, "largo"] = largos[i]
            df.at[idx, "ancho"] = anchos[i]
            df.at[idx, "alto"] = altos[i]
            df.at[idx, "metodo de llegada"] = metodos[i]

        return _ejecutar_transform(df)

    except Exception as e:
        return error_page(
            "CORREGIR",
            "Error al revalidar los datos corregidos",
            f"No se pudieron aplicar las correcciones: {e}",
            stage_hint="transform",
        )


# Load
@app.route("/load", methods=["POST"])
def load():

    archivo = session.get(  # Recuperamos la ruta del archivo CSV con los registros validos guardada en la sesión
        "archivo_validos"
    )

    if not archivo or not os.path.exists(archivo):
        return error_page(
            "SIN DATOS",
            "No hay datos válidos para cargar",
            "Primero debes completar Transform con al menos un registro válido.",
            stage_hint="load",
        )

    try:

        resultado = cargar_datos(  # Logica desde Load_flask.py
            archivo
        )

        return render_template(  # Se envian a load.html los resultados de la carga

            "load.html",

            insertados=resultado["insertados"],  # Cantidad de registros insertados

            omitidos=resultado["omitidos"],  # Cantidad de registros omitidos

            errores=resultado["errores"],  # Cantidad de registros con errores

            mensajes=resultado["mensajes"]  # Lista de mensajes de cada registro procesado para mostrarlo en la interfaz web
        )

    except Exception as e:
        return error_page(
            type(e).__name__,
            "Error durante Load",
            f"No se pudo completar la carga: {e}",
            stage_hint="load",
        )


# ---------------------------------------------------------------------
# Paquetes: consulta, filtros y edición para el cliente/operador
# ---------------------------------------------------------------------

@app.route("/paquetes")
def paquetes():
    return render_template("paquetes.html")


@app.route("/api/paquetes")
def api_listar_paquetes():

    q = request.args.get("q", "").strip()
    estado = request.args.get("estado", "").strip()
    metodo = request.args.get("metodo", "").strip()
    orden = request.args.get("orden", "desc").strip().lower()
    if orden not in ("asc", "desc"):
        orden = "desc"

    sql = """
        SELECT p.id, p.tracking, p.peso, p.metodo_de_llegada, p.estado,
               p.fecha_de_recepcion, c.nombre AS cliente_nombre,
               cp.nombre AS categoria
        FROM paquetes p
        JOIN clientes c ON p.id_cliente = c.id
        JOIN categoria_productos cp ON p.id_categoria_producto = cp.id
        WHERE 1 = 1
    """
    params = []

    if q:
        sql += " AND (p.tracking LIKE %s OR c.nombre LIKE %s)"
        params += [f"%{q}%", f"%{q}%"]
    if estado:
        sql += " AND p.estado = %s"
        params.append(estado)
    if metodo:
        sql += " AND p.metodo_de_llegada = %s"
        params.append(metodo)

    # orden viene validado contra una lista fija (asc/desc), nunca se
    # concatena texto libre del usuario en el ORDER BY.
    sql += f" ORDER BY p.fecha_de_recepcion {orden.upper()} LIMIT 300"

    try:
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                cursor.execute(sql, params)
                filas = cursor.fetchall()
        finally:
            conexion.close()

        for f in filas:
            if f.get("fecha_de_recepcion"):
                f["fecha_de_recepcion"] = f["fecha_de_recepcion"].strftime("%Y-%m-%d %H:%M")
            if f.get("peso") is not None:
                f["peso"] = float(f["peso"])

        return jsonify({"paquetes": filas})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/paquetes/<int:id_paquete>")
def api_detalle_paquete(id_paquete):

    try:
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:

                cursor.execute(
                    """
                    SELECT p.*, c.nombre AS cliente_nombre, c.cedula_pasaporte
                    FROM paquetes p
                    JOIN clientes c ON p.id_cliente = c.id
                    WHERE p.id = %s
                    """,
                    (id_paquete,)
                )
                paquete = cursor.fetchone()

                if not paquete:
                    return jsonify({"error": "Paquete no encontrado"}), 404

                cursor.execute(
                    """
                    SELECT nombre AS categoria FROM categoria_productos
                    WHERE id = %s
                    """,
                    (paquete["id_categoria_producto"],)
                )
                cat = cursor.fetchone()
                paquete["categoria"] = cat["categoria"] if cat else None

                cursor.execute(
                    """
                    SELECT estado, fecha, comentario
                    FROM tracking_eventos
                    WHERE id_paquete = %s
                    ORDER BY fecha ASC
                    """,
                    (id_paquete,)
                )
                eventos = cursor.fetchall()

                # Zona del cliente vía su casillero, y tarifa de esa zona
                # (columna zonas.tarifa) -- ya no se usa la tabla "tarifas".
                cursor.execute(
                    """
                    SELECT z.id AS id_zona, z.nombre AS zona_nombre, z.tarifa AS zona_tarifa
                    FROM casilleros cs
                    JOIN zonas z ON cs.id_zona = z.id
                    WHERE cs.id_cliente = %s
                    LIMIT 1
                    """,
                    (paquete["id_cliente"],)
                )
                zona = cursor.fetchone()

                tarifa = None
                if zona and zona.get("zona_tarifa") is not None:
                    tarifa = {
                        "precio": zona["zona_tarifa"],
                        "tipo_servicio": f"Tarifa de {zona['zona_nombre']}",
                    }

        finally:
            conexion.close()

        # Normalizar tipos para que jsonify no truene con Decimal/datetime
        for campo in ("peso", "largo", "ancho", "alto"):
            if paquete.get(campo) is not None:
                paquete[campo] = float(paquete[campo])
        if paquete.get("fecha_de_recepcion"):
            paquete["fecha_de_recepcion"] = paquete["fecha_de_recepcion"].strftime("%Y-%m-%d %H:%M")

        for ev in eventos:
            if ev.get("fecha"):
                ev["fecha"] = ev["fecha"].strftime("%Y-%m-%d %H:%M")

        if tarifa and tarifa.get("precio") is not None:
            tarifa["precio"] = float(tarifa["precio"])

        return jsonify({
            "paquete": paquete,
            "eventos": eventos,
            "zona": zona,
            "tarifa": tarifa,
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/paquetes/<int:id_paquete>", methods=["PUT"])
def api_actualizar_paquete(id_paquete):

    datos = request.get_json(force=True, silent=True) or {}

    estado_nuevo = datos.get("estado")
    metodo_nuevo = datos.get("metodo_de_llegada")

    if estado_nuevo and estado_nuevo not in ESTADOS_VALIDOS:
        return jsonify({"error": f"Estado '{estado_nuevo}' no es válido"}), 400
    if metodo_nuevo and metodo_nuevo not in METODOS_VALIDOS:
        return jsonify({"error": f"Método '{metodo_nuevo}' no es válido"}), 400

    try:
        peso = float(datos.get("peso"))
    except (TypeError, ValueError):
        return jsonify({"error": "El peso debe ser un número"}), 400

    def _num_o_none(valor):
        try:
            return float(valor) if valor not in (None, "") else None
        except (TypeError, ValueError):
            return None

    largo = _num_o_none(datos.get("largo"))
    ancho = _num_o_none(datos.get("ancho"))
    alto = _num_o_none(datos.get("alto"))
    descripcion = datos.get("descripcion")

    try:
        conexion = obtener_conexion()
        estado_cambio = False
        cliente_info = None
        tracking_actual = None

        try:
            with conexion.cursor() as cursor:

                cursor.execute(
                    "SELECT estado, id_cliente, tracking FROM paquetes WHERE id = %s",
                    (id_paquete,)
                )
                actual = cursor.fetchone()
                if not actual:
                    return jsonify({"error": "Paquete no encontrado"}), 404

                tracking_actual = actual["tracking"]
                estado_cambio = bool(estado_nuevo and estado_nuevo != actual["estado"])

                if estado_cambio:
                    cursor.execute(
                        "SELECT nombre, correo FROM clientes WHERE id = %s",
                        (actual["id_cliente"],)
                    )
                    cliente_info = cursor.fetchone()

                cursor.execute(
                    """
                    UPDATE paquetes
                    SET peso = %s, largo = %s, ancho = %s, alto = %s,
                        metodo_de_llegada = %s, descripcion = %s, estado = %s
                    WHERE id = %s
                    """,
                    (
                        peso, largo, ancho, alto,
                        metodo_nuevo, descripcion, estado_nuevo,
                        id_paquete,
                    )
                )

                if estado_cambio:
                    cursor.execute(
                        """
                        INSERT INTO tracking_eventos (id_paquete, estado, comentario)
                        VALUES (%s, %s, %s)
                        """,
                        (id_paquete, estado_nuevo, "Actualizado manualmente desde el panel")
                    )

            conexion.commit()
        except Exception:
            conexion.rollback()
            raise
        finally:
            conexion.close()

        # Notificacion por correo: solo si el estado realmente cambio y el
        # usuario no desmarco la casilla "notificar" en el panel de edicion.
        resultado_email = None
        notificar = datos.get("notificar", True)
        if estado_cambio and notificar and cliente_info:
            enviado, msg = notificar_cambio_estado(
                cliente_info["nombre"], cliente_info["correo"], tracking_actual, estado_nuevo
            )
            resultado_email = {"enviado": enviado, "mensaje": msg}

        return jsonify({"ok": True, "email": resultado_email})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/paquetes/<int:id_paquete>/notificar", methods=["POST"])
def api_notificar_paquete(id_paquete):
    """Reenvia manualmente, desde la GUI, el correo correspondiente al
    estado actual del paquete (botón "Reenviar notificación")."""

    try:
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT p.tracking, p.estado,
                           c.nombre AS cliente_nombre, c.correo AS cliente_correo
                    FROM paquetes p
                    JOIN clientes c ON p.id_cliente = c.id
                    WHERE p.id = %s
                    """,
                    (id_paquete,)
                )
                fila = cursor.fetchone()
        finally:
            conexion.close()

        if not fila:
            return jsonify({"error": "Paquete no encontrado"}), 404

        enviado, msg = notificar_cambio_estado(
            fila["cliente_nombre"], fila["cliente_correo"], fila["tracking"], fila["estado"]
        )
        return jsonify({"enviado": enviado, "mensaje": msg})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/paquetes/<int:id_paquete>", methods=["DELETE"])
def api_eliminar_paquete(id_paquete):
    """Elimina un paquete individual. Primero borra sus filas dependientes
    (tracking_eventos, envio_paquete) porque tienen FOREIGN KEY hacia
    paquetes sin ON DELETE CASCADE -- si no se borran antes, MariaDB
    rechaza el DELETE de paquetes por violacion de llave foranea."""

    try:
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                cursor.execute("SELECT id FROM paquetes WHERE id = %s", (id_paquete,))
                if not cursor.fetchone():
                    return jsonify({"error": "Paquete no encontrado"}), 404

                cursor.execute("DELETE FROM envio_paquete WHERE id_paquete = %s", (id_paquete,))
                cursor.execute("DELETE FROM tracking_eventos WHERE id_paquete = %s", (id_paquete,))
                cursor.execute("DELETE FROM paquetes WHERE id = %s", (id_paquete,))

            conexion.commit()
        except Exception:
            conexion.rollback()
            raise
        finally:
            conexion.close()

        return jsonify({"ok": True})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/paquetes", methods=["DELETE"])
def api_eliminar_todos_paquetes():
    """Elimina TODOS los paquetes de la base de datos (y sus filas
    dependientes). Accion destructiva pensada para limpiar datos de
    prueba -- la confirmacion se hace del lado del cliente (GUI)."""

    try:
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) AS total FROM paquetes")
                total = cursor.fetchone()["total"]

                cursor.execute("DELETE FROM envio_paquete")
                cursor.execute("DELETE FROM tracking_eventos")
                cursor.execute("DELETE FROM paquetes")

            conexion.commit()
        except Exception:
            conexion.rollback()
            raise
        finally:
            conexion.close()

        return jsonify({"ok": True, "eliminados": total})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":

    app.run(debug=True)