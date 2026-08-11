module.exports = (err, req, res, next) => {
  console.error('🔥 Error en la API:', err);

  res.status(err.statusCode || 500).json({
    exito: false,
    mensaje: err.message || 'Error interno del servidor en Panamá Express'
  });
};