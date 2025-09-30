-- Crear la base de datos
CREATE DATABASE empresa_db;
USE empresa_db;

-- Tabla de clientes
CREATE TABLE cliente (
    id_cliente INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL
) ENGINE=NDBCLUSTER;

-- Tabla de contactos (relacionada con cliente)
CREATE TABLE contacto (
    id_contacto INT AUTO_INCREMENT PRIMARY KEY,
    id_cliente INT,
    telefono VARCHAR(20),
    FOREIGN KEY (id_cliente) REFERENCES cliente(id_cliente) ON DELETE CASCADE
) ENGINE=NDBCLUSTER;

-- Tabla de empleados
CREATE TABLE empleado (
    id_empleado INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    puesto VARCHAR(50) NOT NULL
) ENGINE=NDBCLUSTER;