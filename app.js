const express = require('express');
const cors = require('cors');
require('dotenv').config();

const sequelize = require('./config/database');
const errorHandler = require('./middlewares/errorHandler');

const paqueteRoutes = require('./routes/paqueteRoutes');
const trackingRoutes = require('./routes/trackingRoutes');

const app = express();

// Middlewares globales
app.use(cors());
app.use(express.json());

// Ruta de prueba inicial
app.get('/', (req, res) => {
  res.send('API Panama Express funcionando correctamente 🚀');
});

// Registro de endpoints principales
app.use('/api/paquetes', paqueteRoutes);
app.use('/api/tracking', trackingRoutes);

// Middleware de manejo centralizado de errores
app.use(errorHandler);

const PORT = process.env.PORT || 3000;

// Sincronizar modelos con la base de datos y levantar el servidor
sequelize.sync({ alter: true })
  .then(() => {
    console.log('✅ Conexión exitosa y 📁 Tablas sincronizadas.');
    app.listen(PORT, () => {
      console.log(`🚀 Servidor de Panama Express corriendo en http://localhost:${PORT}`);
    });
  })
  .catch((err) => {
    console.error('❌ Error al sincronizar la base de datos:', err);
  });