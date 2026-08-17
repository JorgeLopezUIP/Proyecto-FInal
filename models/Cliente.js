const { DataTypes } = require('sequelize');
const sequelize = require('../config/database');

const Cliente = sequelize.define('Cliente', {
  id: {
    type: DataTypes.INTEGER,
    primaryKey: true,
    autoIncrement: true
  },

  nombre: {
    type: DataTypes.STRING(255),
    allowNull: false
  },

  cedula_pasaporte: {
    type: DataTypes.STRING(50),
    allowNull: true
  },

  correo: {
    type: DataTypes.STRING(255),
    allowNull: true
  },

  telefono: {
    type: DataTypes.STRING(20),
    allowNull: true
  }

}, {
  tableName: 'clientes',
  timestamps: false
});

module.exports = Cliente;