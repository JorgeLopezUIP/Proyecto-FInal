from conexion import *

conexion = obtener_conexion()
cursor = conexion.cursor()

cursor.execute("""INSERT INTO clientes
(nombre, cedula_pasaporte, correo, telefono)
VALUES
('Juan Pérez', '8-100-1000', 'juan.perez@email.com', '6000-1001'),
('Ana López', '8-100-1001', 'ana.lopez@email.com', '6000-1002'),
('Carlos Díaz', '8-100-1002', 'carlos.diaz@email.com', '6000-1003'),
('María González', '8-100-1003', 'maria.gonzalez@email.com', '6000-1004'),
('Pedro Rodríguez', '8-100-1004', 'pedro.rodriguez@email.com', '6000-1005'),
('Luis Martínez', '8-100-1005', 'luis.martinez@email.com', '6000-1006'),
('Luis Gómez', '8-100-1006', 'luis.gomez@email.com', '6000-1007'),
('Pedro Ruiz', '8-100-1007', 'pedro.ruiz@email.com', '6000-1008'),
('María López', '8-100-1008', 'maria.lopez@email.com', '6000-1009'),
('Ana Torres', '8-100-1009', 'ana.torres@email.com', '6000-1010');
 """)


cursor.execute("""INSERT INTO casilleros
(id_cliente, codigo, direccion)
VALUES
(
    (SELECT id FROM clientes WHERE cedula_pasaporte = '8-100-1000'),
    'MIA-JP001',
    'Miami, Florida'
),
(
    (SELECT id FROM clientes WHERE cedula_pasaporte = '8-100-1001'),
    'MIA-AL002',
    'Miami, Florida'
),
(
    (SELECT id FROM clientes WHERE cedula_pasaporte = '8-100-1002'),
    'MIA-CD003',
    'Miami, Florida'
),
(
    (SELECT id FROM clientes WHERE cedula_pasaporte = '8-100-1003'),
    'MIA-MG004',
    'Miami, Florida'
),
(
    (SELECT id FROM clientes WHERE cedula_pasaporte = '8-100-1004'),
    'MIA-PR005',
    'Miami, Florida'
),
(
    (SELECT id FROM clientes WHERE cedula_pasaporte = '8-100-1005'),
    'MIA-LM006',
    'Miami, Florida'
);""")


cursor.execute("""INSERT INTO bodegas
(nombre, ciudad, direccion)
VALUES
(
    'Bodega Miami',
    'Miami',
    '1234 NW 25th Street, Miami, Florida'
);""")


cursor.execute("""INSERT INTO categoria_productos
(nombre, descripcion)
VALUES
('Electronico', 'Productos electrónicos'),
('Ropa', 'Prendas de vestir'),
('Libro', 'Libros y material de lectura'),
('Accesorios', 'Accesorios para diferentes productos'),
('Calzado', 'Productos de calzado'),
('Otros', 'Productos que no pertenecen a otra categoría');""")

conexion.commit()
cursor.close()
conexion.close()

print("Datos agregados")
