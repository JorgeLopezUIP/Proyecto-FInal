from conexion import *

conexion = obtener_conexion()
cursor = conexion.cursor()

cursor.execute("""INSERT INTO paquetes
(id_cliente, id_bodega, id_categoria_producto, nombre, tracking, peso, largo, ancho, alto, descripcion, estado)
VALUES
(
(SELECT id FROM clientes WHERE cedula_pasaporte = '8-100-1000'),
(SELECT id FROM bodegas WHERE nombre = 'Bodega Miami'),
(SELECT id FROM categoria_productos WHERE nombre = 'Electronico'),
'Laptop',
'DUMMY001',
2.50,
35.00,
25.00,
3.00,
'Computadora portátil Lenovo',
'recibido en bodega'
),
(
(SELECT id FROM clientes WHERE cedula_pasaporte = '8-100-1001'),
(SELECT id FROM bodegas WHERE nombre = 'Bodega Miami'),
(SELECT id FROM categoria_productos WHERE nombre = 'Ropa'),
'Camisa',
'DUMMY002',
0.80,
30.00,
25.00,
5.00,
'Camisa deportiva',
'en transito'
),
(
(SELECT id FROM clientes WHERE cedula_pasaporte = '8-100-1002'),
(SELECT id FROM bodegas WHERE nombre = 'Bodega Miami'),
(SELECT id FROM categoria_productos WHERE nombre = 'Accesorios'),
'Teclado',
'DUMMY003',
1.20,
45.00,
15.00,
5.00,
'Teclado mecánico',
'en aduana'
),
(
(SELECT id FROM clientes WHERE cedula_pasaporte = '8-100-1003'),
(SELECT id FROM bodegas WHERE nombre = 'Bodega Miami'),
(SELECT id FROM categoria_productos WHERE nombre = 'Calzado'),
'Zapatos',
'DUMMY004',
2.00,
35.00,
25.00,
15.00,
'Zapatos deportivos',
'listo para retiro'
),
(
(SELECT id FROM clientes WHERE cedula_pasaporte = '8-100-1004'),
(SELECT id FROM bodegas WHERE nombre = 'Bodega Miami'),
(SELECT id FROM categoria_productos WHERE nombre = 'Electronico'),
'Monitor',
'DUMMY005',
5.50,
70.00,
45.00,
15.00,
'Monitor Samsung',
'en transito'
),
(
(SELECT id FROM clientes WHERE cedula_pasaporte = '8-100-1005'),
(SELECT id FROM bodegas WHERE nombre = 'Bodega Miami'),
(SELECT id FROM categoria_productos WHERE nombre = 'Otros'),
'Cartera',
'DUMMY006',
0.50,
30.00,
20.00,
10.00,
'Cartera de cuero',
'recibido en bodega'
);""")

cursor.execute("""INSERT INTO tracking_eventos
(id_paquete, estado, comentario)
VALUES
(
(SELECT id FROM paquetes WHERE tracking = 'DUMMY001'),
'recibido en bodega',
'Paquete recibido en Bodega Miami'
),
(
(SELECT id FROM paquetes WHERE tracking = 'DUMMY002'),
'recibido en bodega',
'Paquete recibido y registrado'
),
(
(SELECT id FROM paquetes WHERE tracking = 'DUMMY002'),
'en transito',
'Paquete enviado desde Miami'
),
(
(SELECT id FROM paquetes WHERE tracking = 'DUMMY003'),
'recibido en bodega',
'Paquete recibido en Bodega Miami'
),
(
(SELECT id FROM paquetes WHERE tracking = 'DUMMY003'),
'en transito',
'Paquete salió de la bodega'
),
(
(SELECT id FROM paquetes WHERE tracking = 'DUMMY003'),
'en aduana',
'Paquete ingresó a revisión aduanera'
),
(
(SELECT id FROM paquetes WHERE tracking = 'DUMMY004'),
'recibido en bodega',
'Paquete recibido en Bodega Miami'
),
(
(SELECT id FROM paquetes WHERE tracking = 'DUMMY004'),
'en transito',
'Paquete enviado hacia Panamá'
),
(
(SELECT id FROM paquetes WHERE tracking = 'DUMMY004'),
'listo para retiro',
'Paquete disponible para retiro'
);""")

cursor.execute("""INSERT INTO zonas
(nombre, descripcion)
VALUES
(
'Ciudad de Panamá',
'Área metropolitana de Ciudad de Panamá'
),
(
'Panamá Oeste',
'Distritos de Panamá Oeste'
),
(
'Panamá Norte',
'Zona norte de la provincia de Panamá'
),
(
'Panamá Este',
'Zona este de la provincia de Panamá'
);""")

cursor.execute("""INSERT INTO tarifas
(id_zona, peso_min, peso_max, precio, tipo_servicio, vigente)
VALUES
(
(SELECT id FROM zonas WHERE nombre = 'Ciudad de Panamá'),
0.01,
1.00,
5.00,
'Entrega estándar',
TRUE
),
(
(SELECT id FROM zonas WHERE nombre = 'Ciudad de Panamá'),
1.01,
5.00,
8.00,
'Entrega estándar',
TRUE
),
(
(SELECT id FROM zonas WHERE nombre = 'Panamá Oeste'),
0.01,
1.00,
6.00,
'Entrega estándar',
TRUE
),
(
(SELECT id FROM zonas WHERE nombre = 'Panamá Oeste'),
1.01,
5.00,
10.00,
'Entrega estándar',
TRUE
),
(
(SELECT id FROM zonas WHERE nombre = 'Panamá Este'),
0.01,
1.00,
6.50,
'Entrega estándar',
TRUE
),
(
(SELECT id FROM zonas WHERE nombre = 'Panamá Norte'),
0.01,
1.00,
6.00,
'Entrega estándar',
TRUE
);""")

cursor.execute("""INSERT INTO envios
(direccion_de_envio, direccion_de_recibo, fecha_envio, fecha_entrega)
VALUES
(
'Bodega Miami, Miami, Florida',
'Ciudad de Panamá, Panamá',
'2026-08-01 09:00:00',
'2026-08-05 14:00:00'
),
(
'Bodega Miami, Miami, Florida',
'La Chorrera, Panamá Oeste',
'2026-08-03 10:00:00',
NULL
),
(
'Bodega Miami, Miami, Florida',
'San Miguelito, Panamá',
'2026-08-04 08:30:00',
NULL
),
(
'Bodega Miami, Miami, Florida',
'David, Chiriquí',
'2026-08-02 11:00:00',
'2026-08-08 16:00:00'
);""")

cursor.execute("""INSERT INTO envio_paquete
(id_envio, id_paquete)
VALUES
(
(SELECT id FROM envios WHERE id = 1),
(SELECT id FROM paquetes WHERE tracking = 'DUMMY001')
),
(
(SELECT id FROM envios WHERE id = 1),
(SELECT id FROM paquetes WHERE tracking = 'DUMMY005')
),
(
(SELECT id FROM envios WHERE id = 2),
(SELECT id FROM paquetes WHERE tracking = 'DUMMY002')
),
(
(SELECT id FROM envios WHERE id = 2),
(SELECT id FROM paquetes WHERE tracking = 'DUMMY006')
),
(
(SELECT id FROM envios WHERE id = 3),
(SELECT id FROM paquetes WHERE tracking = 'DUMMY003')
),
(
(SELECT id FROM envios WHERE id = 4),
(SELECT id FROM paquetes WHERE tracking = 'DUMMY004')
);""")

cursor.execute("""INSERT INTO facturas
(id_envio, id_cliente, precio)
VALUES
(
(SELECT id FROM envios WHERE id = 1),
(SELECT id FROM clientes WHERE cedula_pasaporte = '8-100-1000'),
13.00
),
(
(SELECT id FROM envios WHERE id = 2),
(SELECT id FROM clientes WHERE cedula_pasaporte = '8-100-1001'),
16.00
),
(
(SELECT id FROM envios WHERE id = 3),
(SELECT id FROM clientes WHERE cedula_pasaporte = '8-100-1002'),
8.00
),
(
(SELECT id FROM envios WHERE id = 4),
(SELECT id FROM clientes WHERE cedula_pasaporte = '8-100-1003'),
20.00
);""")

cursor.execute("""INSERT INTO pagos
(id_factura, monto, metodo_pago, estado)
VALUES
(
(SELECT id FROM facturas WHERE id_envio = 1),
13.00,
'tarjeta de credito',
'pago'
),
(
(SELECT id FROM facturas WHERE id_envio = 2),
16.00,
'yappy',
'pago'
),
(
(SELECT id FROM facturas WHERE id_envio = 3),
8.00,
'efectivo',
'no pago'
),
(
(SELECT id FROM facturas WHERE id_envio = 4),
20.00,
'tarjeta de credito',
'pago'
);""")

conexion.commit()
cursor.close()
conexion.close()

print("Datos dummy agregados")