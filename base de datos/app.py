from flask import Flask, render_template, request, session
import pandas as pd
import os
import uuid
from datetime import datetime
from Transform_flask import transformar_datos
from Load_flask import cargar_datos


app = Flask(__name__)

# En producción, define SECRET_KEY como variable de entorno.
app.secret_key = os.environ.get("SECRET_KEY", "clave-secreta")


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


# Transform
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
        df = pd.read_excel(archivo)

        # Logica desde Transform_flask.py
        resultado = transformar_datos(df)

        # Se separan los registros validos e invalidos
        df_validos = resultado["validos"]
        df_invalidos = resultado["invalidos"]

        # Se guarda el archivo CSV con los registros validos para luego cargarlos en la base de datos
        archivo_validos = os.path.abspath("datos/Datos_validos.csv")

        df_validos.to_csv(
            archivo_validos,
            index=False,
            encoding="utf-8-sig"
        )

        # Guardamos la ruta del archivo CSV con los registros validos para LOAD
        session["archivo_validos"] = archivo_validos

        # Se muestran los resultados
        return render_template(

            "transform.html",

            total=len(df),  # Cantidad de registros originales

            validos=len(df_validos),  # Cantidad de registros validos

            invalidos=len(df_invalidos),  # Cantidad de registros invalidos

            duplicados=resultado["duplicados"],  # Cantidad de registros duplicados

            cedulas_invalidas=(
                resultado["cedulas_invalidas"]  # Cantidad de registros con cédulas inválidas
            ),

            pesos_invalidos=(
                resultado["pesos_invalidos"]  # Cantidad de registros con pesos inválidos
            ),

            tabla_validos=df_validos.to_html(  # Tabla HTML con los registros validos para mostrarlo en la interfaz web
                classes="tabla",
                index=False
            ),

            tabla_invalidos=df_invalidos.to_html(  # Tabla HTML con los registros invalidos para mostrarlo en la interfaz web
                classes="tabla",
                index=False
            )
        )

    except Exception as e:
        return error_page(
            "TRANSFORM",
            "Error durante Transform",
            f"No se pudieron validar los datos: {e}",
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


if __name__ == "__main__":

    app.run(debug=True)
