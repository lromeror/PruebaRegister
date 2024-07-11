create database railway;
use railway;

create table personas (
    id_persona int auto_increment primary key,
    nombre varchar(255),
    apellido varchar(255),
    telefono_movil varchar(255),
    ocupacion enum('estudiante', 'profesional'),
    correo_electronico varchar(255),
    asistencia boolean default 0,
    comida boolean default 0,
    actualizacion boolean default 0
);

create table estudiantes (
    id_persona int,
    carrera varchar(255),
    universidad varchar(255),
    foreign key (id_persona) references personas(id_persona) on delete cascade
);

create table profesionales (
    id_persona int,
    organizacion varchar(255),
    trabajo varchar(255),
    foreign key (id_persona) references personas(id_persona) on delete cascade
);

create table historial (
    id_historial int auto_increment primary key,
    id_persona int,
    fecha_hora timestamp default current_timestamp,
    foreign key (id_persona) references personas(id_persona) on delete cascade
);

delimiter //
create trigger after_register
after insert on personas
for each row
begin
    insert into historial (id_persona) values (new.id_persona);
end;
//

delimiter ;

delimiter //
create trigger after_update_register
after update on personas
for each row
begin
    insert into historial (id_persona) values (new.id_persona);
end;
//
delimiter ;
