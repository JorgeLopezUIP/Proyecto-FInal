from conexion import *

conexion = obtener_conexion()
cursor = conexion.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS clientes (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(255) NOT NULL,
    cedula_pasaporte VARCHAR(50) NOT NULL UNIQUE,
    correo VARCHAR(255) NOT NULL UNIQUE,
    telefono VARCHAR(20) NOT NULL
); """)

cursor.execute("""CREATE TABLE IF NOT EXISTS categoria_productos(
	id INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(255) NOT NULL UNIQUE,
    descripcion VARCHAR(255) 
); """)

cursor.execute("""CREATE TABLE IF NOT EXISTS casilleros (
    id INT PRIMARY KEY AUTO_INCREMENT,
    id_cliente INT NOT NULL,
    codigo VARCHAR(50) NOT NULL UNIQUE,
    direccion VARCHAR(255) NOT NULL,

    FOREIGN KEY (id_cliente) REFERENCES clientes(id)
); """)

cursor.execute("""CREATE TABLE IF NOT EXISTS bodegas (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(100) NOT NULL,
    ciudad VARCHAR(100) NOT NULL,
    direccion VARCHAR(255) NOT NULL
); """)

cursor.execute("""CREATE TABLE IF NOT EXISTS paquetes(
	id INT PRIMARY KEY AUTO_INCREMENT,
    id_cliente INT NOT NULL,
    id_bodega INT NOT NULL,
    id_categoria_producto INT NOT NULL,
    nombre VARCHAR(255) NOT NULL,
    
	tracking VARCHAR(100) NOT NULL UNIQUE,
    peso DECIMAL(10,2) NOT NULL,
    largo DECIMAL(10,2),
    ancho DECIMAL(10,2),
    alto DECIMAL(10,2),
    descripcion VARCHAR(255),
    
    estado ENUM(
		'recibido en bodega', 
		'en transito', 
		'en aduana', 
		'listo para retiro') NOT NULL DEFAULT 'recibido en bodega',
    
    fecha_de_recepcion DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (id_cliente) REFERENCES clientes(id),
    FOREIGN KEY (id_bodega) REFERENCES bodegas(id),
	FOREIGN KEY (id_categoria_producto) REFERENCES categoria_productos(id)
); """)

cursor.execute("""CREATE TABLE IF NOT EXISTS tracking_eventos (
    id INT PRIMARY KEY AUTO_INCREMENT,
    id_paquete INT NOT NULL,
    estado ENUM(
        'recibido en bodega',
        'en transito',
        'en aduana',
        'listo para retiro',
        'entregado'
    ) NOT NULL DEFAULT 'recibido en bodega',
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
    comentario VARCHAR(255),

    FOREIGN KEY (id_paquete) REFERENCES paquetes(id)
); """)

cursor.execute("""CREATE TABLE IF NOT EXISTS envios(
	id INT PRIMARY KEY AUTO_INCREMENT,
    direccion_de_envio VARCHAR(255) NOT NULL, 
    direccion_de_recibo VARCHAR(255) NOT NULL, 
    fecha_envio DATETIME,
    fecha_entrega DATETIME
    
); """)

cursor.execute("""CREATE TABLE IF NOT EXISTS envio_paquete (
    id_envio INT NOT NULL,
    id_paquete INT NOT NULL,

    PRIMARY KEY (id_envio, id_paquete),

    FOREIGN KEY (id_envio) REFERENCES envios(id),
    FOREIGN KEY (id_paquete) REFERENCES paquetes(id)
); """)

cursor.execute("""CREATE TABLE IF NOT EXISTS zonas (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    descripcion VARCHAR(255)
); """)

cursor.execute("""CREATE TABLE IF NOT EXISTS tarifas (
    id INT PRIMARY KEY AUTO_INCREMENT,
    id_zona INT NOT NULL,
    peso_min DECIMAL(10,2) NOT NULL,
    peso_max DECIMAL(10,2) NOT NULL,
    precio DECIMAL(10,2) NOT NULL,
    tipo_servicio VARCHAR(100) NOT NULL,
    vigente BOOLEAN DEFAULT TRUE,
    
    FOREIGN KEY (id_zona) REFERENCES zonas(id)
); """)

cursor.execute("""CREATE TABLE IF NOT EXISTS facturas(
	id INT PRIMARY KEY AUTO_INCREMENT,
    id_envio INT NOT NULL UNIQUE,
    id_cliente INT NOT NULL, 
    precio DECIMAL(10,2) NOT NULL, 
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (id_envio) REFERENCES envios(id),
    FOREIGN KEY (id_cliente) REFERENCES clientes(id)
); """)

cursor.execute("""CREATE TABLE IF NOT EXISTS pagos(
	id INT PRIMARY KEY AUTO_INCREMENT,
    id_factura INT NOT NULL,
    monto DECIMAL(10,2) NOT NULL,
    metodo_pago ENUM('tarjeta de credito', 'efectivo', 'yappy'),
    fecha_pago DATETIME DEFAULT CURRENT_TIMESTAMP,
    estado ENUM('no pago', 'pago') DEFAULT 'no pago' NOT NULL,
    
    FOREIGN KEY (id_factura) REFERENCES facturas(id)
) """)

conexion.commit()
cursor.close()
conexion.close()

print("Datos agregados a la base de datos")


