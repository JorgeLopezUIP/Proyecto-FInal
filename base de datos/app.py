from flask import Flask, render_template, request, session
import pandas as pd
import os
from Transform_flask import transformar_datos
from Load_flask import cargar_datos


app = Flask(__name__)

app.secret_key = "clave-secreta"



#Inicio
@app.route("/") #Ruta donde el usuario selecciona el archivo Excel para iniciar el proceso ETL
def index():

    return render_template("index.html")



#Extract
@app.route("/extract", methods=["POST"])
def extract():

    archivo = request.files.get("archivo") #Se almacena la direccion del archivo seleccionado

    if not archivo or archivo.filename == "":
        return "Ningún archivo seleccionado"

    try:

        #Pandas transforma el Excel en un DataFrame para poder manipularlo y graficarlo en la consola
        df = pd.read_excel(archivo)

        #Se crea la carpeta datos si no existe
        os.makedirs(
            "datos",
            exist_ok=True
        )

        #Ubicacion temporal
        archivo_excel = os.path.abspath(
            "datos/archivo_original.xlsx"
        )

        df.to_excel(
            archivo_excel,
            index=False
        )


        # Guardamos la ruta para TRANSFORM
        session["archivo_excel"] = archivo_excel


        
        #Se convierte el dataframe en una tabla HTML para mostrarlo en la interfaz web
        return render_template(

            "extract.html",

            total=len(df),

            columnas=len(df.columns),

            tabla=df.to_html(
                classes="tabla",
                index=False
            )
        )


    except Exception as e:

        return f"Error durante EXTRACT: {e}"



#Transform
@app.route("/transform", methods=["POST"])
def transform():

    #Recuperamos la ruta del archivo Excel guardada en la sesión
    archivo = session.get("archivo_excel")


    if not archivo or not os.path.exists(archivo):

        return (
            "No hay ningún archivo extraído. "
            "Primero debes realizar EXTRACT."
        )


    try:

        #Pandas transforma el Excel en un DataFrame para poder manipularlo y graficarlo en la consola
        df = pd.read_excel(archivo)

        #Logica desde Transform_flask.py
        resultado = transformar_datos(df)

        #Se separan los registros validos e invalidos
        df_validos = resultado["validos"]
        df_invalidos = resultado["invalidos"]

        #Se guarda el archivo CSV con los registros validos para luego cargarlos en la base de datos
        archivo_validos = os.path.abspath(
            "datos/Datos_validos.csv"
        )


        df_validos.to_csv(
            archivo_validos,
            index=False,
            encoding="utf-8-sig"
        )

        # Guardamos la ruta del archivo CSV con los registros validos para LOAD
        session["archivo_validos"] = archivo_validos

        #Se muestran los resultados
        return render_template(

            "transform.html",

            total=len(df), #Cantidad de registros originales

            validos=len(df_validos), #Cantidad de registros validos

            invalidos=len(df_invalidos), #Cantidad de registros invalidos

            duplicados=resultado["duplicados"], #Cantidad de registros duplicados

            cedulas_invalidas=(
                resultado["cedulas_invalidas"] #Cantidad de registros con cédulas inválidas
            ),

            pesos_invalidos=(
                resultado["pesos_invalidos"] #Cantidad de registros con pesos inválidos
            ),

            tabla_validos=df_validos.to_html( #Tabla HTML con los registros validos para mostrarlo en la interfaz web
                classes="tabla",
                index=False
            ),

            tabla_invalidos=df_invalidos.to_html( #Tabla HTML con los registros invalidos para mostrarlo en la interfaz web
                classes="tabla",
                index=False
            )
        )


    except Exception as e:

        return f"Error durante TRANSFORM: {e}"



#Load
@app.route("/load", methods=["POST"])
def load():

    archivo = session.get( #Recuperamos la ruta del archivo CSV con los registros validos guardada en la sesión
        "archivo_validos"
    )


    if not archivo or not os.path.exists(archivo):

        return "No hay datos válidos para cargar"


    try:

        resultado = cargar_datos( #Logica desde Load_flask.py
            archivo
        )


        return render_template( #Se enviant a load.html los resultados de la carga

            "load.html",

            insertados=resultado["insertados"], #Cantidad de registros insertados

            omitidos=resultado["omitidos"], #Cantidad de registros omitidos

            errores=resultado["errores"], #Cantidad de registros con errores

            mensajes=resultado["mensajes"] #Lista de mensajes de cada registro procesado para mostrarlo en la interfaz web
        )


    except Exception as e:

        return f"Error durante LOAD: {type(e).__name__}: {e}"



if __name__ == "__main__":

    app.run(debug=True)