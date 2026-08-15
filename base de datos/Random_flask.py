import random
import uuid
import pandas as pd

# Mismos clientes que ya existen en la BD (seed de clientes), para que la
# mayoria de los paquetes generados encuentren su cliente real al hacer Load.
CLIENTES_SEED = [
    ("Juan Pérez", "8-100-1000"),
    ("Ana López", "8-100-1001"),
    ("Carlos Díaz", "8-100-1002"),
    ("María González", "8-100-1003"),
    ("Pedro Rodríguez", "8-100-1004"),
    ("Luis Martínez", "8-100-1005"),
    ("Luis Gómez", "8-100-1006"),
    ("Pedro Ruiz", "8-100-1007"),
    ("María López", "8-100-1008"),
    ("Ana Torres", "8-100-1009"),
]

# Cada descripcion cae en la categoria que clasificar_producto() de
# Transform_flask.py ya sabe reconocer por palabra clave.
PRODUCTOS = {
    "Electronico": [
        "Laptop Dell Inspiron", "Tablet Samsung Galaxy", "Monitor LG 24 pulgadas",
        "Televisor Sony 43 pulgadas", "Consola PS5", "Impresora HP Deskjet",
        "Camara Canon EOS",
    ],
    "Ropa": [
        "Camisa azul manga larga", "Vestido negro de fiesta",
        "Pantalon jean clasico", "Blusa blanca formal",
    ],
    "Calzado": ["Zapato deportivo Nike", "Zapato casual Adidas"],
    "Accesorios": [
        "Mouse inalambrico Logitech", "Teclado mecanico Redragon",
        "Audifono Bluetooth JBL", "Smartwatch Apple",
    ],
    "Otros": ["Juguete de coleccion", "Set de cocina", "Lampara de escritorio"],
}

METODOS = ["aereo", "maritimo", "terrestre"]


def _cedula_con_errata(cedula):
    """Erratas que transformar_datos() sabe corregir: espacios, puntos en vez
    de guiones, guiones dobles y minusculas."""
    errata = random.choice(["ok", "espacios", "puntos", "doble_guion", "minuscula"])
    if errata == "espacios":
        return " " + cedula.replace("-", " - ") + " "
    if errata == "puntos":
        return cedula.replace("-", ".")
    if errata == "doble_guion":
        return cedula.replace("-", "--")
    if errata == "minuscula":
        return cedula.lower()
    return cedula


def _tracking_con_errata(tracking):
    """Erratas que transformar_datos() corrige: minusculas, guiones de mas,
    espacios sobrantes."""
    errata = random.choice(["ok", "minuscula", "guion", "espacios"])
    if errata == "minuscula":
        return tracking.lower()
    if errata == "guion":
        return tracking[:3] + "-" + tracking[3:]
    if errata == "espacios":
        return f"  {tracking}  "
    return tracking


def _metodo_con_errata(metodo):
    """transformar_datos() solo hace strip(); la normalizacion de mayusculas
    la hace Load_flask.py al insertar, asi que aqui se puede ensuciar el
    casing libremente sin que se rompa el pipeline."""
    errata = random.choice(["ok", "mayuscula", "espacios", "capitalizado"])
    if errata == "mayuscula":
        return metodo.upper()
    if errata == "espacios":
        return f"  {metodo}  "
    if errata == "capitalizado":
        return metodo.capitalize()
    return metodo


def _cliente_con_errata(nombre):
    """transformar_datos() aplica str.title(), asi que el casing de entrada
    no importa."""
    errata = random.choice(["ok", "mayuscula", "minuscula", "espacios"])
    if errata == "mayuscula":
        return nombre.upper()
    if errata == "minuscula":
        return nombre.lower()
    if errata == "espacios":
        return f"  {nombre}  "
    return nombre


def generar_paquetes_aleatorios(cantidad=20, tasa_invalidos=0.15, semilla=None):
    """
    Genera un DataFrame con las mismas columnas que espera /extract
    (Tracking, Cedula, Cliente, Descripcion, Peso, Metodo de llegada).

    La mayoria de las filas llevan erratas "sucias" pero solucionables por
    transformar_datos() (mayusculas/minusculas, espacios, puntos y guiones
    dobles en la cedula, etc). Una fraccion minoritaria (tasa_invalidos) es
    realmente invalida a proposito -- cedula mal formada, peso <= 0 o
    tracking duplicado -- para poder probar tambien el bucket de invalidos,
    igual que en el excel de ejemplo original.
    """
    if semilla is not None:
        random.seed(semilla)

    filas = []
    trackings_usados = []

    for i in range(1, cantidad + 1):
        nombre, cedula = random.choice(CLIENTES_SEED)
        categoria = random.choice(list(PRODUCTOS.keys()))
        descripcion = random.choice(PRODUCTOS[categoria])
        metodo = random.choice(METODOS)
        peso = round(random.uniform(0.3, 14.0), 2)
        # Sufijo aleatorio (no secuencial): si el tracking fuera "AMZ001",
        # "AMZ002"... cada vez que se genera un lote nuevo se repiten los
        # mismos codigos que lotes anteriores ya cargados en la base de
        # datos, y la mayoria termina "OMITIDO: ya existe" al hacer Load.
        tracking_base = "AMZ" + uuid.uuid4().hex[:6].upper()

        cedula_final = _cedula_con_errata(cedula)

        if random.random() < tasa_invalidos:
            tipo_falla = random.choice(["cedula_mala", "peso_malo", "duplicado"])
            if tipo_falla == "cedula_mala":
                cedula_final = "X" + str(random.randint(100, 999))  # no matchea el patron valido
            elif tipo_falla == "peso_malo":
                peso = random.choice([0, -2.5])
            elif tipo_falla == "duplicado" and trackings_usados:
                tracking_base = random.choice(trackings_usados)

        filas.append({
            "Tracking": _tracking_con_errata(tracking_base),
            "Cedula": cedula_final,
            "Cliente": _cliente_con_errata(nombre),
            "Descripcion": f"  {descripcion}  " if random.random() < 0.3 else descripcion,
            "Peso": peso,
            "Metodo de llegada": _metodo_con_errata(metodo),
        })
        trackings_usados.append(tracking_base)

    return pd.DataFrame(filas)
