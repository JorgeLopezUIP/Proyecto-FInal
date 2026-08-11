const express = require('express');
const router = express.Router();

// IMPORTANTE: Extraer la función con destructuración {}
const { obtenerTracking } = require('../controllers/trackingController');

// Definir la ruta
router.get('/:tracking', obtenerTracking);

module.exports = router;