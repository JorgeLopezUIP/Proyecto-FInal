const { DataTypes } = require('sequelize');
const sequelize = require('../config/database');
const Cliente = require('./Cliente');

const Paquete = sequelize.define('Paquete', {

  id: {
    type: DataTypes.INTEGER,
    primaryKey: true,
    autoIncrement: true
  },

  id_cliente: {
    type: DataTypes.INTEGER,
    allowNull: false
  },

  id_bodega: {
    type: DataTypes.INTEGER,
    allowNull: false
  },

  id_categoria_producto: {
    type: DataTypes.INTEGER,
    allowNull: false
  },

  nombre: {
    type: DataTypes.STRING(255),
    allowNull: false
  },

  tracking: {
    type: DataTypes.STRING(100),
    allowNull: false,
    unique: true
  },

  peso: {
    type: DataTypes.DECIMAL(10, 2),
    allowNull: false
  },

  largo: {
    type: DataTypes.DECIMAL(10, 2)
  },

  ancho: {
    type: DataTypes.DECIMAL(10, 2)
  },

  alto: {
    type: DataTypes.DECIMAL(10, 2)
  },

  metodo_de_llegada: {
    type: DataTypes.ENUM(
      'aereo',
      'maritimo',
      'terrestre'
    ),
    allowNull: false
  },

  descripcion: {
    type: DataTypes.STRING(255)
  },

  estado: {
    type: DataTypes.ENUM(
      'recibido en bodega',
      'en transito',
      'en aduana',
      'listo para retiro'
    ),
    allowNull: false,
    defaultValue: 'recibido en bodega'
  },

  fecha_de_recepcion: {
    type: DataTypes.DATE,
    defaultValue: DataTypes.NOW
  }

}, {
  tableName: 'paquetes',
  timestamps: false
});

Cliente.hasMany(Paquete, {
  foreignKey: 'id_cliente'
});

Paquete.belongsTo(Cliente, {
  foreignKey: 'id_cliente'
});

module.exports = Paquete;