CREATE TABLE Usuario (
					    email               VARCHAR(80)    NOT NULL,
					    docPais             VARCHAR(25)    NOT NULL,
					    docTipo             VARCHAR(15)    NOT NULL,
					    docNumero           VARCHAR(20)    NOT NULL,
					    dirPais             VARCHAR(35)    NOT NULL,
					    dirLocalidad        VARCHAR(35)    NOT NULL,
					    dirCalle            VARCHAR(40)    NOT NULL,
					    dirNumero           VARCHAR(20)    NOT NULL,
					    dirCodigoPostal     VARCHAR(20)    NOT NULL,
						passw VARCHAR(64) NOT NULL,
 
    CONSTRAINT PK_Usuario    PRIMARY KEY (email),
    CONSTRAINT UQ_Documento  UNIQUE (dirPais, docTipo, docNumero)
);


CREATE TABLE Usuario_Telefono (
							    email       VARCHAR(80)    NOT NULL,
							    telefono    VARCHAR(25)    NOT NULL,
							 
							    CONSTRAINT PK_UsuarioTelefono   PRIMARY KEY (email, telefono),
							    CONSTRAINT FK_UT_Usuario        FOREIGN KEY (email) REFERENCES Usuario(email) ON DELETE CASCADE ON UPDATE CASCADE
);	


CREATE TABLE Administrador_Pais_Sede (
									    email               VARCHAR(80)    NOT NULL,
									    paisJurisdiccion    VARCHAR(25)     NOT NULL,
									    fechaAsignacionCargo DATE           NOT NULL,
									 
									    CONSTRAINT PK_Admin     PRIMARY KEY (email),
									    CONSTRAINT FK_Admin_User   FOREIGN KEY (email) REFERENCES Usuario(email) ON DELETE CASCADE ON UPDATE CASCADE
);


CREATE TABLE Funcionario_Validacion (
									    email          VARCHAR(80)    NOT NULL,
									    numeroLegajo   VARCHAR(25)     NOT NULL,
									 
									    CONSTRAINT PK_Funcionario   PRIMARY KEY (email),
									    CONSTRAINT UQ_Legajo        UNIQUE (numeroLegajo),
									    CONSTRAINT FK_Fun_User      FOREIGN KEY (email) REFERENCES Usuario(email) ON DELETE CASCADE ON UPDATE CASCADE
);


CREATE TABLE Usuario_General (
							    email                VARCHAR(80)    NOT NULL,
							    fechaRegistro        DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP,
							    estadoVerifIdentidad ENUM('pendiente','verificado','rechazado') NOT NULL DEFAULT 'pendiente',
							 
							    CONSTRAINT PK_UsuarioGeneral    PRIMARY KEY (email),
							    CONSTRAINT FK_UG_User           FOREIGN KEY (email) REFERENCES Usuario(email) ON DELETE CASCADE ON UPDATE CASCADE
);


CREATE TABLE Estadio (
					    idEstadio           INT            NOT NULL AUTO_INCREMENT,
					    nombre              VARCHAR(80)    NOT NULL,
					    pais                VARCHAR(30)    NOT NULL,
					    ciudad              VARCHAR(50)    NOT NULL,
						emailAdmin          VARCHAR(80)    NOT NULL,   -- administrador responsable (1:N)
						fechaAsignacion     DATE           NOT NULL,   -- cuándo fue asignado el admin
					 
    CONSTRAINT PK_Estadio   PRIMARY KEY (idEstadio),
	CONSTRAINT FK_Est_Admin     FOREIGN KEY (emailAdmin) REFERENCES Administrador_Pais_Sede(email) ON UPDATE CASCADE
);


CREATE TABLE Sector (
						idSector            INT             NOT NULL AUTO_INCREMENT,
						idEstadio           INT             NOT NULL,
						codigo              CHAR(1)         NOT NULL,
						capacidadMaxima     INT             NOT NULL,
						costoEntrada        DECIMAL(10,2)   NOT NULL,

						CONSTRAINT PK_Sector_idSector PRIMARY KEY (idSector), 
						
						CONSTRAINT UQ_Sector_idEstadio_codigo UNIQUE (idEstadio, codigo),
						
						CONSTRAINT FK_Sector_idEstadio_referencias_Estadio FOREIGN KEY (idEstadio) REFERENCES Estadio(idEstadio) ON UPDATE CASCADE,
						
						CONSTRAINT CHK_Sector_codigo CHECK (codigo IN ('A','B','C','D')),
						
						CONSTRAINT CHK_Sector_capacidadMaxima CHECK (capacidadMaxima > 0),
						
						CONSTRAINT CHK_Sector_costoEntrada CHECK (costoEntrada >= 0)
);

CREATE TABLE Equipo (
					    idEquipo            INT             NOT NULL AUTO_INCREMENT,
					    nombre              VARCHAR(60)     NOT NULL,
					    paisOrigen          VARCHAR(40)     NOT NULL,
					 
					    CONSTRAINT PK_Equipo    PRIMARY KEY (idEquipo),
					    CONSTRAINT UQ_Equipo    UNIQUE (nombre)
);

CREATE TABLE Evento (
					    idEvento            INT             NOT NULL AUTO_INCREMENT,
					    nombreEvento        VARCHAR(100)    NOT NULL,
					    fecha               DATE            NOT NULL,
					    hora                TIME            NOT NULL,
					    idEstadio           INT             NOT NULL,
					    emailAdmin          VARCHAR(80)    NOT NULL,   -- quien realizó el alta del evento
					 
					    CONSTRAINT PK_Evento        PRIMARY KEY (idEvento),
					    CONSTRAINT FK_Evento_Est    FOREIGN KEY (idEstadio) REFERENCES Estadio(idEstadio) ON UPDATE CASCADE,
					    CONSTRAINT FK_Evento_Admin  FOREIGN KEY (emailAdmin) REFERENCES Administrador_Pais_Sede(email) ON UPDATE CASCADE,
					    CONSTRAINT UQ_Evento_Slot   UNIQUE (idEstadio, fecha, hora)
);


CREATE TABLE Evento_Equipo (
								idEvento INT NOT NULL,
								idEquipo INT NOT NULL,
								rol ENUM('local','visitante') NOT NULL,
							 
								CONSTRAINT PK_EventoEquipo_idEvento_idEquipo PRIMARY KEY (idEvento, idEquipo),
								
								CONSTRAINT FK_EventoEquipo_idEvento_ref_Evento FOREIGN KEY (idEvento) REFERENCES Evento(idEvento) ON UPDATE CASCADE,
								
								CONSTRAINT FK_EventoEquipo_idEquipo_ref_Equipo FOREIGN KEY (idEquipo) REFERENCES Equipo(idEquipo) ON UPDATE CASCADE,
								
								-- garantiza a lo sumo un local y un visitante por evento
								CONSTRAINT UQ_EventoEquipo_rol UNIQUE (idEvento, rol)
);
						

CREATE TABLE Evento_Sector (
								idEvento INT NOT NULL,
								idSector INT NOT NULL,
							 
								CONSTRAINT PK_EventoSector_idEvento_idSector PRIMARY KEY (idEvento, idSector),
								
								CONSTRAINT FK_EventoSector_idEvento_referencias_Evento FOREIGN KEY (idEvento) REFERENCES Evento(idEvento) ON UPDATE CASCADE,
								
								CONSTRAINT FK_EventoSector_idSector_referencias_Sector FOREIGN KEY (idSector) REFERENCES Sector(idSector) ON UPDATE CASCADE
);
 


CREATE TABLE Venta (
				    idVenta INT NOT NULL AUTO_INCREMENT,
				    numero  VARCHAR(50) NOT NULL,
				    fechaVenta DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
				    estado     ENUM('pendiente','confirmada','paga') NOT NULL DEFAULT 'pendiente',
				    montoTotal DECIMAL(12,2)   NOT NULL DEFAULT 0.00,
				    emailComprador VARCHAR(80) NOT NULL,
				 
				    CONSTRAINT PK_Venta_idVenta PRIMARY KEY (idVenta),
					
					CONSTRAINT UQ_Venta_numero UNIQUE (numero),
				    
				    CONSTRAINT FK_Venta_emailComprador_ref_UsuarioGeneral FOREIGN KEY (emailComprador) REFERENCES Usuario_General(email) ON UPDATE CASCADE
);


CREATE TABLE Entrada (
						idEntrada INT NOT NULL AUTO_INCREMENT,
						idVenta   INT NOT NULL,
						idEvento  INT NOT NULL,
						idSector  INT NOT NULL,
						emailPropietario VARCHAR(80) NOT NULL,
						estado    ENUM('activa','consumida','transferencia_pendiente') NOT NULL DEFAULT 'activa',
						cantTransferencias  INT NOT NULL DEFAULT 0,
					 
						CONSTRAINT PK_Entrada_idEntrada PRIMARY KEY (idEntrada),
						
						CONSTRAINT FK_Entrada_idVenta_ref_Venta FOREIGN KEY (idVenta) REFERENCES Venta(idVenta) ON UPDATE CASCADE,
						
						CONSTRAINT FK_Entrada_idEvento_idSector_ref_EventoSector FOREIGN KEY (idEvento, idSector) REFERENCES Evento_Sector(idEvento, idSector) ON UPDATE CASCADE,
						
						CONSTRAINT FK_Entrada_emailPropietario_ref_UsuarioGeneral FOREIGN KEY (emailPropietario) REFERENCES Usuario_General(email) ON UPDATE CASCADE,
						
						CONSTRAINT CHK_Entrada_cantTransferencias CHECK (cantTransferencias <= 3)
);


CREATE TABLE Transferencia (
							    idTransferencia 	INT NOT NULL AUTO_INCREMENT,
							    idEntrada       	INT             NOT NULL,
							    emailOrigen     	VARCHAR(80)     NOT NULL,
							    emailDestino    	VARCHAR(80)     NOT NULL,
							    fechaTransferencia  DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
							    estado              ENUM('pendiente','aceptada','rechazada') NOT NULL DEFAULT 'pendiente',
							 
							    CONSTRAINT PK_Transferencia_idTransferencia PRIMARY KEY (idTransferencia),
							    
							    CONSTRAINT FK_Transferencia_idEntrada_ref_Entrada FOREIGN KEY (idEntrada) REFERENCES Entrada(idEntrada) ON UPDATE CASCADE,
							    
							    CONSTRAINT FK_Transferencia_emailOrigen_ref_UsuarioGeneral FOREIGN KEY (emailOrigen) REFERENCES Usuario_General(email),
							    
							    CONSTRAINT FK_Transferencia_emailDestino_ref_UsuarioGeneral FOREIGN KEY (emailDestino) REFERENCES Usuario_General(email),
							    
							    CONSTRAINT CHK_Transferencia_origenDistintoDestino CHECK (emailOrigen <> emailDestino)
);


CREATE TABLE Token_QR (
					    idToken   INT NOT NULL AUTO_INCREMENT,
					    idEntrada INT NOT NULL,
					    valor     VARCHAR(250) NOT NULL,
					    fechaHoraGenerado   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
					    tiempoVencimiento   INT NOT NULL DEFAULT 30,  -- segundos
					    estado              ENUM('activo','expirado','usado') NOT NULL DEFAULT 'activo',
					 
					    CONSTRAINT PK_TokenQR_idToken PRIMARY KEY (idToken),
					    
					    CONSTRAINT FK_TokenQR_idEntrada_ref_Entrada FOREIGN KEY (idEntrada) REFERENCES Entrada(idEntrada) ON UPDATE CASCADE
);


CREATE TABLE Dispositivo (
						    idDispositivo INT NOT NULL AUTO_INCREMENT,
						    dirMAC        VARCHAR(20) NOT NULL,
						    emailFuncionario VARCHAR(80) NOT NULL,
						 
						    CONSTRAINT PK_Dispositivo_idDispositivo PRIMARY KEY (idDispositivo),
						    
						    CONSTRAINT UQ_Dispositivo_dirMAC UNIQUE (dirMAC),
						    
						    CONSTRAINT FK_Dispositivo_emailFuncionario_ref_Funcionario FOREIGN KEY (emailFuncionario) REFERENCES Funcionario_Validacion(email) ON UPDATE CASCADE
);


CREATE TABLE Validacion_Entrada (
									idValidacion INT NOT NULL AUTO_INCREMENT,
									idEntrada    INT NOT NULL,
									idToken      INT NOT NULL,
									idDispositivo INT NOT NULL,
									emailFuncionario VARCHAR(80) NOT NULL,
									fechaHoraValidacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
								 
									CONSTRAINT PK_ValEntrada_idValidacion PRIMARY KEY (idValidacion),
									
									CONSTRAINT UQ_ValidacionAcceso_idEntrada UNIQUE (idEntrada),
									
									CONSTRAINT FK_ValidacionAcceso_idEntrada_ref_Entrada FOREIGN KEY (idEntrada) REFERENCES Entrada(idEntrada) ON UPDATE CASCADE,
									
									CONSTRAINT FK_ValidacionAcceso_idToken_ref_TokenQR   FOREIGN KEY (idToken)   REFERENCES Token_QR(idToken) ON UPDATE CASCADE,
									
									CONSTRAINT FK_ValidacionAcceso_idDispositivo_ref_Dispositivo  FOREIGN KEY (idDispositivo) REFERENCES Dispositivo(idDispositivo) ON UPDATE CASCADE,
									
									CONSTRAINT FK_ValidacionAcceso_emailFuncionario_referencias_Funcionario FOREIGN KEY (emailFuncionario) REFERENCES Funcionario_Validacion(email) ON UPDATE CASCADE
);

CREATE TABLE Asignacion_Funcionario (
									    idEvento INT NOT NULL,
									    idSector INT NOT NULL,
									    emailFuncionario VARCHAR(80) NOT NULL,
									    
									    CONSTRAINT PK_FuncAsig PRIMARY KEY (idEvento, idSector, emailFuncionario),
									    
									    CONSTRAINT FK_FuncAsig_Evento FOREIGN KEY (idEvento) REFERENCES Evento(idEvento),
									    
									    CONSTRAINT FK_FuncAsig_Sector FOREIGN KEY (idSector) REFERENCES Sector(idSector),
									    
									    CONSTRAINT FK_FuncAsig_Func FOREIGN KEY (emailFuncionario) REFERENCES Funcionario_Validacion(email)
);


CREATE TABLE Tasa_Comision (
							    idTasa     INT NOT NULL AUTO_INCREMENT,
							    porcentaje DECIMAL(5,2) NOT NULL,
							    fechaDesde DATE NOT NULL,
							    fechaHasta DATE NULL,
							    
								CONSTRAINT PK_TasaComision PRIMARY KEY (idTasa)
);


--INSERTS


INSERT INTO Usuario (email, docPais, docTipo, docNumero, dirPais, dirLocalidad, dirCalle, dirNumero, dirCodigoPostal, passw) VALUES
('juan.perez@gmail.com','Uruguay','CI','12345678', 'Uruguay', 'Montevideo', 'Av. 18 de Julio', '1234', '11200', SHA2('password123',256)),
('maria.garcia@gmail.com', 'Uruguay', 'CI', '23456789', 'Uruguay',   'Montevideo', 'Bulevar Artigas',  '567',  '11300', SHA2('password123',256)),
('carlos.lopez@gmail.com', 'Argentina', 'DNI','30123456', 'Argentina', 'Buenos Aires','Av. Corrientes',  '800',  'C1043', SHA2('password123',256)),
('ana.martinez@gmail.com', 'Uruguay', 'CI', '34567890', 'Uruguay',   'Montevideo', 'Av. Italia', '2300', '11600', SHA2('password123',256)),
('pedro.rodriguez@gmail.com',  'Mexico',    'INE','ROMP850101','Mexico',   'Ciudad de Mexico','Insurgentes','450',  '06600', SHA2('password123',256)),
('lucia.fernandez@gmail.com',  'Uruguay',   'CI', '45678901', 'Uruguay',   'Paysandu',   'Calle Leandro Gomez','123','60000', SHA2('password123',256)),
('santiago.trinidad@gmail.com',  'Uruguay',   'CI', '44050580', 'Uruguay',   'Colonia',   'Uruguay','583','11111', SHA2('password123',256)),
('diego.gamarra@gmail.com',  'Uruguay',   'CI', '44455520', 'Uruguay',   'Canelones',   'Calle Leandro Jimenez','1311','8882', SHA2('password123',256)),
('rodrigo.pereira@gmail.com',  'Uruguay',   'CI', '54854811', 'Uruguay',   'Maldonado',   'Calle Lindolfo Gomez','8982','11166', SHA2('password123',256)),
('ximena.romano@gmail.com',  'Uruguay',   'CI', '56524530', 'Uruguay',   'Treinta y Tres',   '19 de abril','778','46000', SHA2('password123',256)),
('sebastian.colina@gmail.com',  'Argentina',   'CI', '16094582', 'Uruguay',   'Montevideo',   'Bv. España','4411','11200', SHA2('password123',256)),
('admin.usa@fifa.com',         'USA',       'SSN','111223333','USA',       'New York',   '5th Avenue',       '350',  '10001', SHA2('adminpass',256)),
('admin.mex@fifa.com',         'Mexico',    'INE','GOMA900202','Mexico',   'Ciudad de Mexico','Reforma',     '222',  '06600', SHA2('password123',256)),
('func.est1@fifa.com',         'USA',       'SSN','222334444','USA',       'Los Angeles','Sunset Blvd',      '100',  '90028', SHA2('password123',256)),
('func.est2@fifa.com',         'Mexico',    'INE','LOPH880303','Mexico',   'Monterrey',  'Av. Constitucion', '500',  '64000', SHA2('password123',256));
 
 
INSERT INTO Usuario_Telefono (email, telefono) VALUES
('juan.perez@gmail.com',       '+598 99 111 222'),
('juan.perez@gmail.com',       '+598 99 333 444'),   -- juan tiene 2 telefonos
('maria.garcia@gmail.com',     '+598 98 555 666'),
('carlos.lopez@gmail.com',     '+54 11 4444 5555'),
('ana.martinez@gmail.com',     '+598 99 777 888'),
('pedro.rodriguez@gmail.com',  '+52 55 1234 5678'),
('lucia.fernandez@gmail.com',  '+598 47 123 456'),
('admin.usa@fifa.com',         '+1 212 555 0100'),
('admin.mex@fifa.com',         '+52 55 9876 5432'),
('func.est1@fifa.com',         '+1 310 555 0200');
 
 
INSERT INTO Administrador_Pais_Sede (email, paisJurisdiccion, fechaAsignacionCargo) VALUES
('admin.usa@fifa.com', 'USA',    '2025-01-15'),
('admin.mex@fifa.com', 'Mexico', '2025-01-15');
 
 
INSERT INTO Funcionario_Validacion (email, numeroLegajo) VALUES
('func.est1@fifa.com', 'LEG-001'),
('func.est2@fifa.com', 'LEG-002');
 
 
INSERT INTO Usuario_General (email, fechaRegistro, estadoVerifIdentidad) VALUES
('juan.perez@gmail.com',      '2026-04-10 09:00:00', 'verificado'),
('maria.garcia@gmail.com',    '2024-01-11 10:30:00', 'verificado'),
('carlos.lopez@gmail.com',    '2020-01-12 11:00:00', 'verificado'),
('ana.martinez@gmail.com',    '2026-01-13 08:45:00', 'pendiente'),
('pedro.rodriguez@gmail.com', '2025-09-14 14:00:00', 'verificado'),
('lucia.fernandez@gmail.com', '2023-01-15 16:30:00', 'verificado');
 
 
INSERT INTO Estadio (nombre, pais, ciudad, emailAdmin, fechaAsignacion) VALUES
('SoFi Stadium',            'USA',    'Los Angeles',     'admin.usa@fifa.com', '2025-02-01'),  
('MetLife Stadium',         'USA',    'New York',        'admin.usa@fifa.com', '2025-02-01'), 
('AT&T Stadium',            'USA',    'Dallas',          'admin.usa@fifa.com', '2025-02-01'),  
('Levi\'s Stadium',         'USA',    'San Francisco',   'admin.usa@fifa.com', '2025-02-01'),  
('Estadio Azteca',          'Mexico', 'Ciudad de Mexico','admin.mex@fifa.com', '2025-02-05'),  
('Estadio BBVA',            'Mexico', 'Monterrey',       'admin.mex@fifa.com', '2025-02-05'), 
('Estadio Akron',           'Mexico', 'Guadalajara',     'admin.mex@fifa.com', '2025-02-05'),  
('BC Place',                'Canada', 'Vancouver',       'admin.usa@fifa.com', '2025-02-10'),  
('BMO Field',               'Canada', 'Toronto',         'admin.usa@fifa.com', '2025-02-10'), 
('Stade Olympique',         'Canada', 'Montreal',        'admin.usa@fifa.com', '2025-02-10');  
 
 
INSERT INTO Sector (idEstadio, codigo, capacidadMaxima, costoEntrada) VALUES
(1, 'A', 5000,  500.00),   
(1, 'B', 10000, 300.00),   
(1, 'C', 15000, 150.00),   
(1, 'D', 20000, 80.00),    
(2, 'A', 4000,  600.00),   
(2, 'B', 8000,  350.00),   
(5, 'A', 6000,  700.00),   
(5, 'B', 12000, 400.00),   
(5, 'C', 18000, 200.00),   
(5, 'D', 25000, 100.00);   
 
 
INSERT INTO Equipo (nombre, paisOrigen) VALUES
('Uruguay',    'Uruguay'),
('Argentina',  'Argentina'),
('Brasil',     'Brasil'),
('Francia',    'Francia'),
('Alemania',   'Alemania'),
('España',     'España'),
('Portugal',   'Portugal'),
('Inglaterra', 'Inglaterra'),
('Mexico',     'Mexico'),
('USA',        'USA');
 
 
INSERT INTO Evento (nombreEvento, fecha, hora, idEstadio, emailAdmin) VALUES
('Uruguay vs Portugal',    '2026-06-15', '18:00:00', 1, 'admin.usa@fifa.com'),  
('Argentina vs Francia',   '2026-06-16', '18:00:00', 1, 'admin.usa@fifa.com'),  
('Brasil vs Alemania',     '2026-06-17', '18:00:00', 2, 'admin.usa@fifa.com'),  
('España vs Inglaterra',   '2026-06-18', '18:00:00', 2, 'admin.usa@fifa.com'),  
('Mexico vs USA',          '2026-06-19', '20:00:00', 5, 'admin.mex@fifa.com'),  
('Uruguay vs Argentina',   '2026-06-22', '20:00:00', 1, 'admin.usa@fifa.com'),  
('Francia vs Brasil',      '2026-06-23', '18:00:00', 2, 'admin.usa@fifa.com'), 
('Portugal vs España',     '2026-06-24', '18:00:00', 5, 'admin.mex@fifa.com'),  
('Alemania vs Inglaterra', '2026-06-25', '20:00:00', 5, 'admin.mex@fifa.com'),  
('Mexico vs Argentina',    '2026-06-26', '20:00:00', 5, 'admin.mex@fifa.com');  
 
 
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
(5, 10,'visitante');
 
 
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
('VTA-0001', '2026-02-01 10:00:00', 'paga',       0.00, 'juan.perez@gmail.com'),       
('VTA-0002', '2026-02-02 11:00:00', 'paga',       0.00, 'maria.garcia@gmail.com'),     
('VTA-0003', '2026-02-03 12:00:00', 'paga',       0.00, 'carlos.lopez@gmail.com'),     
('VTA-0004', '2026-02-04 13:00:00', 'confirmada', 0.00, 'ana.martinez@gmail.com'),     
('VTA-0005', '2026-02-05 14:00:00', 'paga',       0.00, 'pedro.rodriguez@gmail.com'),  
('VTA-0006', '2026-02-06 15:00:00', 'paga',       0.00, 'lucia.fernandez@gmail.com'),  
('VTA-0007', '2026-02-07 09:00:00', 'pendiente',  0.00, 'juan.perez@gmail.com'),       
('VTA-0008', '2026-02-08 10:30:00', 'paga',       0.00, 'maria.garcia@gmail.com'),     
('VTA-0009', '2026-02-09 11:45:00', 'paga',       0.00, 'carlos.lopez@gmail.com'),     
('VTA-0010', '2026-02-10 16:00:00', 'confirmada', 0.00, 'pedro.rodriguez@gmail.com');  
 
 
INSERT INTO Entrada (idVenta, idEvento, idSector, emailPropietario, estado, cantTransferencias) VALUES
(1, 1, 1, 'juan.perez@gmail.com',      'activa', 0),  
(1, 1, 2, 'juan.perez@gmail.com',      'activa', 0),  
(2, 1, 3, 'maria.garcia@gmail.com',    'activa', 0),  
(3, 2, 1, 'carlos.lopez@gmail.com',    'activa', 0),  
(3, 2, 2, 'carlos.lopez@gmail.com',    'activa', 0),  
(4, 3, 5, 'ana.martinez@gmail.com',    'activa', 0),  
(5, 5, 7, 'pedro.rodriguez@gmail.com', 'activa', 0),  
(5, 5, 8, 'pedro.rodriguez@gmail.com', 'activa', 0),  
(6, 5, 9, 'lucia.fernandez@gmail.com', 'activa', 0),  
(8, 1, 2, 'maria.garcia@gmail.com',    'activa', 0);  
 
 
INSERT INTO Transferencia (idEntrada, emailOrigen, emailDestino, fechaTransferencia, estado) VALUES
(1, 'juan.perez@gmail.com',     'maria.garcia@gmail.com',    '2026-03-01 10:00:00', 'pendiente'),
(3, 'maria.garcia@gmail.com',   'carlos.lopez@gmail.com',    '2026-03-02 11:00:00', 'aceptada'),
(9, 'lucia.fernandez@gmail.com','pedro.rodriguez@gmail.com', '2026-03-03 12:00:00', 'rechazada'),
(4, 'carlos.lopez@gmail.com',   'ana.martinez@gmail.com',    '2026-03-04 13:00:00', 'pendiente'),
(6, 'ana.martinez@gmail.com',   'lucia.fernandez@gmail.com', '2026-03-05 14:00:00', 'aceptada'),
(7, 'pedro.rodriguez@gmail.com','juan.perez@gmail.com',      '2026-03-06 15:00:00', 'aceptada'),
(2, 'juan.perez@gmail.com',     'ana.martinez@gmail.com',    '2026-03-07 09:00:00', 'rechazada'),
(5, 'carlos.lopez@gmail.com',   'lucia.fernandez@gmail.com', '2026-03-08 10:00:00', 'pendiente'),
(7, 'pedro.rodriguez@gmail.com','maria.garcia@gmail.com',    '2026-03-09 11:00:00', 'aceptada');
 
 
INSERT INTO Tasa_Comision (porcentaje, fechaDesde, fechaHasta) VALUES
(5.00, '2025-01-01', NULL);