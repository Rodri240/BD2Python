USE TicketWorldCup;

-- Inserts
INSERT INTO Usuario (email, docPais, docTipo, docNumero, dirPais, dirLocalidad, dirCalle, dirNumero, dirCodigoPostal, passw) VALUES
('juan.perez@gmail.com', 'Uruguay', 'CI', '12345678', 'Uruguay', 'Montevideo', 'Av. 18 de Julio', '1234', '11200', SHA2('password123',256)),
('maria.garcia@gmail.com', 'Uruguay', 'CI', '23456789', 'Uruguay', 'Montevideo', 'Bulevar Artigas', '567', '11300', SHA2('password123',256)),
('carlos.lopez@gmail.com', 'Argentina', 'DNI', '30123456', 'Argentina', 'Buenos Aires', 'Av. Corrientes', '800', 'C1043', SHA2('password123',256)),
('ana.martinez@gmail.com', 'Uruguay', 'CI', '34567890', 'Uruguay', 'Montevideo', 'Av. Italia', '2300', '11600', SHA2('password123',256)),
('pedro.rodriguez@gmail.com', 'Mexico', 'INE', 'ROMP850101', 'Mexico', 'Ciudad de Mexico', 'Insurgentes', '450', '06600', SHA2('password123',256)),
('lucia.fernandez@gmail.com', 'Uruguay', 'CI', '45678901', 'Uruguay', 'Paysandu', 'Calle Leandro Gomez', '123', '60000', SHA2('password123',256)),
('santiago.trinidad@gmail.com', 'Uruguay', 'CI', '44050580', 'Uruguay', 'Colonia', 'Uruguay', '583', '11111', SHA2('password123',256)),
('diego.gamarra@gmail.com', 'Uruguay', 'CI', '44455520', 'Uruguay', 'Canelones', 'Calle Leandro Jimenez', '1311', '8882', SHA2('password123',256)),
('rodrigo.pereira@gmail.com', 'Uruguay', 'CI', '54854811', 'Uruguay', 'Maldonado', 'Calle Lindolfo Gomez', '8982', '11166', SHA2('password123',256)),
('ximena.romano@gmail.com', 'Uruguay', 'CI', '56524530', 'Uruguay', 'Treinta y Tres', '19 de abril', '778', '46000', SHA2('password123',256)),
('sebastian.colina@gmail.com', 'Argentina', 'CI', '16094582', 'Uruguay', 'Montevideo', 'Bv. España', '4411', '11200', SHA2('password123',256)),
('admin.usa@fifa.com', 'USA', 'SSN', '111223333', 'USA', 'New York', '5th Avenue', '350', '10001', SHA2('adminpass',256)),
('admin.mex@fifa.com', 'Mexico', 'INE', 'GOMA900202', 'Mexico', 'Ciudad de Mexico', 'Reforma', '222', '06600', SHA2('password123',256)),
('func.est1@fifa.com', 'USA', 'SSN', '222334444', 'USA', 'Los Angeles', 'Sunset Blvd', '100', '90028', SHA2('password123',256)),
('func.est2@fifa.com', 'Mexico', 'INE', 'LOPH880303', 'Mexico', 'Monterrey', 'Av. Constitucion', '500', '64000', SHA2('password123',256));

INSERT INTO Usuario_Telefono (email, telefono) VALUES
('juan.perez@gmail.com', '+598 99 111 222'),
('juan.perez@gmail.com', '+598 99 333 444'),   -- juan tiene 2 telefonos
('maria.garcia@gmail.com', '+598 98 555 666'),
('carlos.lopez@gmail.com', '+54 11 4444 5555'),
('ana.martinez@gmail.com', '+598 99 777 888'),
('pedro.rodriguez@gmail.com', '+52 55 1234 5678'),
('lucia.fernandez@gmail.com', '+598 47 123 456'),
('admin.usa@fifa.com', '+1 212 555 0100'),
('admin.mex@fifa.com', '+52 55 9876 5432'),
('func.est1@fifa.com', '+1 310 555 0200');

INSERT INTO Administrador_Pais_Sede (email, paisJurisdiccion, fechaAsignacionCargo) VALUES
('admin.usa@fifa.com', 'USA', '2025-01-15'),
('admin.mex@fifa.com', 'Mexico', '2025-01-15');

INSERT INTO Funcionario_Validacion (email, numeroLegajo) VALUES
('func.est1@fifa.com', 'LEG-001'),
('func.est2@fifa.com', 'LEG-002');

INSERT INTO Usuario_General (email, fechaRegistro, estadoVerifIdentidad) VALUES
('juan.perez@gmail.com', '2026-04-10 09:00:00', 'verificado'),
('maria.garcia@gmail.com', '2024-01-11 10:30:00', 'verificado'),
('carlos.lopez@gmail.com', '2020-01-12 11:00:00', 'verificado'),
('ana.martinez@gmail.com', '2026-01-13 08:45:00', 'pendiente'),
('pedro.rodriguez@gmail.com', '2025-09-14 14:00:00', 'verificado'),
('lucia.fernandez@gmail.com', '2023-01-15 16:30:00', 'verificado');

INSERT INTO Estadio (nombre, pais, ciudad, emailAdmin, fechaAsignacion) VALUES
('SoFi Stadium', 'USA', 'Los Angeles', 'admin.usa@fifa.com', '2025-02-01'),
('MetLife Stadium', 'USA', 'New York', 'admin.usa@fifa.com', '2025-02-01'),
('AT&T Stadium', 'USA', 'Dallas', 'admin.usa@fifa.com', '2025-02-01'),
('Levi\'s Stadium', 'USA', 'San Francisco', 'admin.usa@fifa.com', '2025-02-01'),
('Estadio Azteca', 'Mexico', 'Ciudad de Mexico', 'admin.mex@fifa.com', '2025-02-05'),
('Estadio BBVA', 'Mexico', 'Monterrey', 'admin.mex@fifa.com', '2025-02-05'),
('Estadio Akron', 'Mexico', 'Guadalajara', 'admin.mex@fifa.com', '2025-02-05'),
('BC Place', 'Canada', 'Vancouver', 'admin.usa@fifa.com', '2025-02-10'),
('BMO Field', 'Canada', 'Toronto', 'admin.usa@fifa.com', '2025-02-10'),
('Stade Olympique', 'Canada', 'Montreal', 'admin.usa@fifa.com', '2025-02-10');

INSERT INTO Sector (idEstadio, codigo, capacidadMaxima, costoEntrada) VALUES
(1, 'A', 5000, 500.00),
(1, 'B', 10000, 300.00),
(1, 'C', 15000, 150.00),
(1, 'D', 20000, 80.00),
(2, 'A', 4000, 600.00),
(2, 'B', 8000, 350.00),
(5, 'A', 6000, 700.00),
(5, 'B', 12000, 400.00),
(5, 'C', 18000, 200.00),
(5, 'D', 25000, 100.00);

INSERT INTO Equipo (nombre, paisOrigen) VALUES
('Uruguay', 'Uruguay'),
('Argentina', 'Argentina'),
('Brasil', 'Brasil'),
('Francia', 'Francia'),
('Alemania', 'Alemania'),
('España', 'España'),
('Portugal', 'Portugal'),
('Inglaterra', 'Inglaterra'),
('Mexico', 'Mexico'),
('USA', 'USA');

INSERT INTO Evento (nombreEvento, fecha, hora, idEstadio, emailAdmin) VALUES
('Uruguay vs Portugal', '2026-06-15', '18:00:00', 1, 'admin.usa@fifa.com'),
('Argentina vs Francia', '2026-06-16', '18:00:00', 1, 'admin.usa@fifa.com'),
('Brasil vs Alemania', '2026-06-17', '18:00:00', 2, 'admin.usa@fifa.com'),
('España vs Inglaterra', '2026-06-18', '18:00:00', 2, 'admin.usa@fifa.com'),
('Mexico vs USA', '2026-06-19', '20:00:00', 5, 'admin.mex@fifa.com'),
('Uruguay vs Argentina', '2026-06-22', '20:00:00', 1, 'admin.usa@fifa.com'),
('Francia vs Brasil', '2026-06-23', '18:00:00', 2, 'admin.usa@fifa.com'),
('Portugal vs España', '2026-06-24', '18:00:00', 5, 'admin.mex@fifa.com'),
('Alemania vs Inglaterra', '2026-06-25', '20:00:00', 5, 'admin.mex@fifa.com'),
('Mexico vs Argentina', '2026-06-26', '20:00:00', 5, 'admin.mex@fifa.com');

INSERT INTO Evento_Equipo (idEvento, idEquipo, rol) VALUES
(1, 1, 'local'),
(1, 7, 'visitante'),
(2, 2, 'local'),
(2, 4, 'visitante'),
(3, 3, 'local'),
(3, 5, 'visitante'),
(4, 6, 'local'),
(4, 8, 'visitante'),
(5, 9, 'local'),
(5, 10, 'visitante');

INSERT INTO Evento_Sector (idEvento, idSector) VALUES
(1, 1),
(1, 2),
(1, 3),
(2, 1),
(2, 2),
(3, 5),
(3, 6),
(5, 7),
(5, 8),
(5, 9);

INSERT INTO Venta (numero, fechaVenta, estado, montoTotal, emailComprador) VALUES
('VTA-0001', '2026-02-01 10:00:00', 'paga', 0.00, 'juan.perez@gmail.com'),
('VTA-0002', '2026-02-02 11:00:00', 'paga', 0.00, 'maria.garcia@gmail.com'),
('VTA-0003', '2026-02-03 12:00:00', 'paga', 0.00, 'carlos.lopez@gmail.com'),
('VTA-0004', '2026-02-04 13:00:00', 'confirmada', 0.00, 'ana.martinez@gmail.com'),
('VTA-0005', '2026-02-05 14:00:00', 'paga', 0.00, 'pedro.rodriguez@gmail.com'),
('VTA-0006', '2026-02-06 15:00:00', 'paga', 0.00, 'lucia.fernandez@gmail.com'),
('VTA-0007', '2026-02-07 09:00:00', 'pendiente', 0.00, 'juan.perez@gmail.com'),
('VTA-0008', '2026-02-08 10:30:00', 'paga', 0.00, 'maria.garcia@gmail.com'),
('VTA-0009', '2026-02-09 11:45:00', 'paga', 0.00, 'carlos.lopez@gmail.com'),
('VTA-0010', '2026-02-10 16:00:00', 'confirmada', 0.00, 'pedro.rodriguez@gmail.com');

INSERT INTO Entrada (idVenta, idEvento, idSector, emailPropietario, estado, cantTransferencias) VALUES
(1, 1, 1, 'juan.perez@gmail.com', 'activa', 0),
(1, 1, 2, 'juan.perez@gmail.com', 'activa', 0),
(2, 1, 3, 'maria.garcia@gmail.com', 'activa', 0),
(3, 2, 1, 'carlos.lopez@gmail.com', 'activa', 0),
(3, 2, 2, 'carlos.lopez@gmail.com', 'activa', 0),
(4, 3, 5, 'ana.martinez@gmail.com', 'activa', 0),
(5, 5, 7, 'pedro.rodriguez@gmail.com', 'activa', 0),
(5, 5, 8, 'pedro.rodriguez@gmail.com', 'activa', 0),
(6, 5, 9, 'lucia.fernandez@gmail.com', 'activa', 0),
(8, 1, 2, 'maria.garcia@gmail.com', 'activa', 0);

INSERT INTO Transferencia (idEntrada, emailOrigen, emailDestino, fechaTransferencia, estado) VALUES
(1, 'juan.perez@gmail.com', 'maria.garcia@gmail.com', '2026-03-01 10:00:00', 'pendiente'),
(3, 'maria.garcia@gmail.com', 'carlos.lopez@gmail.com', '2026-03-02 11:00:00', 'aceptada'),
(9, 'lucia.fernandez@gmail.com', 'pedro.rodriguez@gmail.com', '2026-03-03 12:00:00', 'rechazada'),
(4, 'carlos.lopez@gmail.com', 'ana.martinez@gmail.com', '2026-03-04 13:00:00', 'pendiente'),
(6, 'ana.martinez@gmail.com', 'lucia.fernandez@gmail.com', '2026-03-05 14:00:00', 'aceptada'),
(7, 'pedro.rodriguez@gmail.com', 'juan.perez@gmail.com', '2026-03-06 15:00:00', 'aceptada'),
(2, 'juan.perez@gmail.com', 'ana.martinez@gmail.com', '2026-03-07 09:00:00', 'rechazada'),
(5, 'carlos.lopez@gmail.com', 'lucia.fernandez@gmail.com', '2026-03-08 10:00:00', 'pendiente'),
(7, 'pedro.rodriguez@gmail.com', 'maria.garcia@gmail.com', '2026-03-09 11:00:00', 'aceptada');

INSERT INTO Tasa_Comision (porcentaje, fechaDesde, fechaHasta) VALUES
(5.00, '2025-01-01', NULL);