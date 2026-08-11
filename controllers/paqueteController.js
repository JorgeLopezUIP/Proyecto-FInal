const Paquete = require('../models/Paquete');

// 1. Obtener todos los paquetes
const obtenerPaquetes = async (req, res, next) => {
  try {
    const paquetes = await Paquete.findAll();
    res.status(200).json({ exito: true, datos: paquetes });
  } catch (error) {
    next(error);
  }
};

// 2. Crear paquete
const crearPaquete = async (req, res, next) => {
  try {
    const nuevoPaquete = await Paquete.create(req.body);
    res.status(201).json({ exito: true, datos: nuevoPaquete });
  } catch (error) {
    next(error);
  }
};

// 3. Actualizar paquete
const actualizarPaquete = async (req, res, next) => {
  try {
    const { id } = req.params;
    const paquete = await Paquete.findByPk(id);
    if (!paquete) {
      return res.status(404).json({ exito: false, mensaje: 'Paquete no encontrado' });
    }
    await paquete.update(req.body);
    res.status(200).json({ exito: true, datos: paquete });
  } catch (error) {
    next(error);
  }
};

// 4. Eliminar paquete
const eliminarPaquete = async (req, res, next) => {
  try {
    const { id } = req.params;
    const paquete = await Paquete.findByPk(id);
    if (!paquete) {
      return res.status(404).json({ exito: false, mensaje: 'Paquete no encontrado' });
    }
    await paquete.destroy();
    res.status(200).json({ exito: true, mensaje: 'Paquete eliminado correctamente' });
  } catch (error) {
    next(error);
  }
};

// IMPORTANTE: Todas deben estar dentro de este objeto
module.exports = {
  obtenerPaquetes,
  crearPaquete,
  actualizarPaquete,
  eliminarPaquete
};

