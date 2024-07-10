CREATE DATABASE WIDSESPOL2025;
USE WIDSESPOL2025;

CREATE TABLE Personas (
    id_persona INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(255),
    apellido VARCHAR(255),
    telefono_movil VARCHAR(255),
    ocupacion ENUM('Estudiante', 'Profesional'),
    correo_electronico VARCHAR(255),
	asistencia BOOLEAN DEFAULT 0,
    comida BOOLEAN DEFAULT 0,
    actualizacion BOOLEAN DEFAULT 0
);

CREATE TABLE Estudiantes (
    id_persona INT,
    carrera VARCHAR(255),
    universidad VARCHAR(255),
    FOREIGN KEY (id_persona) REFERENCES Personas(id_persona)
);

CREATE TABLE Profesionales (
    id_persona INT,
    organizacion VARCHAR(255),
    trabajo VARCHAR(255),
    FOREIGN KEY (id_persona) REFERENCES Personas(id_persona)
);

create table Historial(
	id_historial int,
    id_persona int,
    fecha_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_persona) REFERENCES Personas(id_persona)
);

DELIMITER //
CREATE TRIGGER after_register
AFTER INSERT ON Personas
FOR EACH ROW
BEGIN
    INSERT INTO Historial (id_persona) VALUES (NEW.id_persona);
END;
//

DELIMITER ;

DELIMITER //
CREATE TRIGGER after_update_register
AFTER Update on Personas
FOR EACH ROW
BEGIN
    INSERT INTO Historial (id_persona) VALUES (NEW.id_persona);
END;
//
DELIMITER ;