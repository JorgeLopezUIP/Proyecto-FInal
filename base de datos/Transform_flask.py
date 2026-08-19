import pandas as pd
import re
#Transform 
def validar_cedula(cedula):
    patron = r"^(?:\d+-\d+-\d+|\d+-\d+|[EN]-\d+-\d+)$" #Valida que la cedula este en formato correcto

    return bool(re.match(patron,cedula))

def clasificar_producto(descripcion): #Agrega categoria a los productosd ependiendo de su descripcion
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

def calcular_tarifa(peso): #Calcula la tarifa del producto dependiendo de su peso
    if peso <= 1:
        return 5.00
    elif peso <= 5:
        return 8.00
    elif peso <= 10:
        return 12.00
    else:
        return 15.00

def transformar_datos(df):

    df.columns = ( #Estandarizar las columnas
        df.columns
        .astype(str) #Convierte los datos en strings
        .str.strip() #Elimina los espacios en blanco
        .str.lower() #Pone el texto en minusculas
        .str.replace("-", "", regex=False) #Elimina caracteres que sobran
    )

    df["tracking"] = ( #Tabla de tracking
        df["tracking"]
        .astype(str) #Convierte los datos en string
        .str.strip() #Elimina los espacios en blanco
        .str.upper() #Pone el texto en mayusculas
        .str.replace("-", "", regex=False) #Elimina caracteres que sobran
    )

    df["cedula"] = ( #Tabla de cedula
        df["cedula"] 
        .astype(str) #Convierte los datos en string
        .str.strip() #Elimina los espacios en blanco
        .str.upper() #Pone los datos en mayuscula
        .str.replace(" ", "", regex=False) #Elimina espacio entre digitos
        .str.replace(".", "-",regex=False) #Reemplaza puntos por guiones 
        .str.replace("--", "-",regex=False) #Corrige dobles guiones
    )

    df["metodo de llegada"] = ( #Tabla de cedula
        df["metodo de llegada"] 
        .astype(str) #Convierte los datos en string
        .str.strip() #Elimina los espacios en blanco
        )
    

    df["cedula_valida"] = (df["cedula"].apply(validar_cedula)) #Se aplica la funcion para validar cedula 

    df["cliente"] = ( #Tabla de clientes
        df["cliente"]
        .astype(str) #Convierte los datos en string
        .str.strip() #Elimina los espacios en blanco
        .str.title() #Capitaliza la primera letra de cada nombre
    )

    df["descripcion"] = ( #Tabla de descripcion
        df["descripcion"]
        .astype(str) #Convierte los datos en string
        .str.strip() #Elimina los espacios en blanco
    )

    #Tabla peso
    df["peso"] = pd.to_numeric(df["peso"], errors="coerce") #Convierte los datos en numeros
    df["largo"] = pd.to_numeric(df["largo"], errors="coerce") #Convierte los datos en numeros
    df["ancho"] = pd.to_numeric(df["ancho"], errors="coerce") #Convierte los datos en numeros
    df["alto"] = pd.to_numeric(df["alto"], errors="coerce") #Convierte los datos en numeros

    duplicados = df.duplicated(
            subset = ["tracking"],
            keep=False
        
    )

    df_validos = df[df["peso"].notna() & (df["peso"] > 0) & (df["largo"].notna() & (df["largo"] > 0)) & (df["ancho"].notna() & (df["ancho"] > 0)) & (df["alto"].notna() & (df["alto"] > 0)) & (df["cedula_valida"]) & (~duplicados)].copy() #Detecta los pesos validos
    df_invalidos = df[df["peso"].isna() | (df["peso"] <= 0) | (df["largo"].isna() | (df["largo"] <= 0)) | (df["ancho"].isna() | (df["ancho"] <= 0)) | (df["alto"].isna() | (df["alto"] <= 0)) | (~df["cedula_valida"]) | (duplicados)].copy() #Detecta pesos y dimensiones no validos como datos N/A y menores o iguales a 0

    df_validos["categoria"] = df_validos["descripcion"].apply(clasificar_producto) #Se inserta categoria en la tabla
    df_validos["tarifa_preliminar"] = df_validos["peso"].apply(calcular_tarifa) #Se inserta la tarifa en la tabla

    # Motivo por el que cada fila cayó en invalidos -- sin esto, filas que a
    # simple vista se ven bien (ej. cedula y peso correctos) parecen invalidas
    # "sin razon" cuando en realidad el motivo es un tracking duplicado que
    # no se nota porque la otra copia tiene un formato distinto (mayus/guion),
    # o alguna dimension (largo/ancho/alto) vacia o en cero.
    motivos = []
    for i in df_invalidos.index:
        razones = []
        if duplicados.loc[i]:
            razones.append("tracking duplicado")
        if not df.loc[i, "cedula_valida"]:
            razones.append("cedula con formato invalido")
        peso_val = df.loc[i, "peso"]
        if pd.isna(peso_val):
            razones.append("peso no numerico o vacio")
        elif peso_val <= 0:
            razones.append("peso debe ser mayor a 0")
        for campo, etiqueta in (("largo", "largo"), ("ancho", "ancho"), ("alto", "alto")):
            valor = df.loc[i, campo]
            if pd.isna(valor):
                razones.append(f"{etiqueta} no numerico o vacio")
            elif valor <= 0:
                razones.append(f"{etiqueta} debe ser mayor a 0")
        motivos.append("; ".join(razones) if razones else "motivo no identificado")

    df_invalidos["motivo"] = motivos

    df_validos = df_validos.drop(columns=["cedula_valida"])

    df_invalidos = df_invalidos.drop(columns=["cedula_valida"])

    duplicados_count = int(duplicados.sum())

    cedulas_invalidas = int(
        (~df["cedula_valida"]).sum()
    )

    pesos_invalidos = int(
        (
            df["peso"].isna()
            |
            (df["peso"] <= 0)
        ).sum()
    )

    dimensiones_invalidas = int(
        (
            df["largo"].isna() | (df["largo"] <= 0)
            |
            df["ancho"].isna() | (df["ancho"] <= 0)
            |
            df["alto"].isna() | (df["alto"] <= 0)
        ).sum()
    )

    return {

        "validos": df_validos,

        "invalidos": df_invalidos,

        "duplicados": duplicados_count,

        "cedulas_invalidas": cedulas_invalidas,

        "pesos_invalidos": pesos_invalidos,

        "dimensiones_invalidas": dimensiones_invalidas
    }
