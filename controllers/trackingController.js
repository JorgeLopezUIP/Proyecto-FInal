const Paquete = require('../models/Paquete');

const obtenerTracking = async (req, res, next) => {
  try {
    const { tracking } = req.params;

    const paquete = await Paquete.findOne({
      where: { tracking }
    });

    if (!paquete) {
      return res.status(404).json({
        exito: false,
        mensaje: 'Paquete no encontrado'
      });
    }

    res.status(200).json({
      exito: true,
      datos: paquete
    });

  } catch (error) {
    next(error);
  }
};

// IMPORTANTE: Exportar la función como objeto
module.exports = {
  obtenerTracking
};