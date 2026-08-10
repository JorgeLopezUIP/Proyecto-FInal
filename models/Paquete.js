const { DataTypes } = require('sequelize');
const sequelize = require('../config/database');
const Cliente = require('./Cliente');

const Paquete = sequelize.define('Paquete', {
  id: {
    type: DataTypes.INTEGER,
    primaryKey: true,
    autoIncrement: true
  },
  numero_tracking: {
    type: DataTypes.STRING(50),
    allowNull: false,
    unique: true
  },
  peso_lb: {
    type: DataTypes.DECIMAL(8, 2),
    allowNull: false
  },
  descripcion: {
    type: DataTypes.STRING(255)
  },
  estado: {
    type: DataTypes.STRING(30),
    defaultValue: 'MIAMI'
  },
  cliente_id: {
    type: DataTypes.INTEGER,
    references: { model: Cliente, key: 'id' }
  }
}, {
  tableName: 'paquetes',
  timestamps: false
});

// Relación: Un cliente tiene muchos paquetes
Cliente.hasMany(Paquete, { foreignKey: 'cliente_id' });
Paquete.belongsTo(Cliente, { foreignKey: 'cliente_id' });

module.exports = Paquete;