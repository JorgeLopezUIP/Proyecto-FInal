const express = require('express');
const router = express.Router();

// Verifica que los nombres aquí coincidan 100% con los exportados arriba
const { 
  obtenerPaquetes, 
  crearPaquete, 
  actualizarPaquete, 
  eliminarPaquete 
} = require('../controllers/paqueteController');

// Rutas
router.get('/', obtenerPaquetes);
router.post('/', crearPaquete);
router.put('/:id', actualizarPaquete);
router.delete('/:id', eliminarPaquete);

module.exports = router;