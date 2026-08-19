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

cursor.execute("""INSERT INTO zonas
(nombre, descripcion, tarifa)
VALUES
('Zona 1', '0 a 5 km - San Francisco, Paitilla, Obarrio, El Cangrejo y Via España', 4.00),
('Zona 2', '5 a 10 km - Bella Vista, Costa del Este, El Dorado, Parque Lefevre y Rio Abajo', 5.00),
('Zona 3', '10 a 15 km - Brisas del Golf, Clayton, Los Pueblos, Villa Lucre y Santa Maria', 8.00),
('Zona 4', '15 a 20 km - Costa Sur, Versalles, Don Bosco, Las Cumbres y San Antonio', 10.00)
;""")

cursor.execute("""INSERT INTO casilleros
(id_cliente,id_zona, codigo, direccion)
VALUES
(
    (SELECT id FROM clientes WHERE cedula_pasaporte = '8-100-1000'),
    (SELECT id FROM zonas WHERE nombre = 'Zona 1'),
    'MIA-JP001',
    'Paitilla, Panama'
),
(
    (SELECT id FROM clientes WHERE cedula_pasaporte = '8-100-1001'),
    (SELECT id FROM zonas WHERE nombre = 'Zona 1'),
    'MIA-AL002',
    'Obarrio, Panama'
),
(
    (SELECT id FROM clientes WHERE cedula_pasaporte = '8-100-1002'),
    (SELECT id FROM zonas WHERE nombre = 'Zona 2'),
    'MIA-CD003',
    'Bella Vista, Panama'
),
(
    (SELECT id FROM clientes WHERE cedula_pasaporte = '8-100-1003'),
    (SELECT id FROM zonas WHERE nombre = 'Zona 3'),
    'MIA-MG004',
    'Clayton, Panama'
),
(
    (SELECT id FROM clientes WHERE cedula_pasaporte = '8-100-1004'),
    (SELECT id FROM zonas WHERE nombre = 'Zona 4'),
    'MIA-PR005',
    'Don Bosco, Panama'
),
(
    (SELECT id FROM clientes WHERE cedula_pasaporte = '8-100-1005'),
    (SELECT id FROM zonas WHERE nombre = 'Zona 4'),
    'MIA-LM006',
    'Costa Sur, Panama'
),

(
    (SELECT id FROM clientes WHERE cedula_pasaporte = '8-100-1006'),
    (SELECT id FROM zonas WHERE nombre = 'Zona 3'),
    'MIA-LM007',
    'Santa Maria, Panama'
),

(
    (SELECT id FROM clientes WHERE cedula_pasaporte = '8-100-1007'),
    (SELECT id FROM zonas WHERE nombre = 'Zona 3'),
    'MIA-LM008',
    'Villa Lucre, Panama'
),

(
    (SELECT id FROM clientes WHERE cedula_pasaporte = '8-100-1008'),
    (SELECT id FROM zonas WHERE nombre = 'Zona 1'),
    'MIA-LM009',
    'Punta Pacifica, Panama'
),

(
    (SELECT id FROM clientes WHERE cedula_pasaporte = '8-100-1009'),
    (SELECT id FROM zonas WHERE nombre = 'Zona 1'),
    'MIA-LM010',
    'El Cangrejo, Panama'
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
