CREATE DATABASE IF NOT EXISTS TicketWorldCup;
USE TicketWorldCup;

CREATE TABLE Usuario (
    email             VARCHAR(80) NOT NULL,
    docPais           VARCHAR(25) NOT NULL,
    docTipo           VARCHAR(15) NOT NULL,
    docNumero         VARCHAR(20) NOT NULL,
    dirPais           VARCHAR(35) NOT NULL,
    dirLocalidad      VARCHAR(35) NOT NULL,
    dirCalle          VARCHAR(40) NOT NULL,
    dirNumero         VARCHAR(20) NOT NULL,
    dirCodigoPostal   VARCHAR(20) NOT NULL,
    passw             VARCHAR(64) NOT NULL,

    CONSTRAINT PK_Usuario PRIMARY KEY (email),
    CONSTRAINT UQ_Documento UNIQUE (dirPais, docTipo, docNumero)
);

CREATE TABLE Usuario_Telefono (
    email      VARCHAR(80) NOT NULL,
    telefono   VARCHAR(25) NOT NULL,

    CONSTRAINT PK_UsuarioTelefono PRIMARY KEY (email, telefono),
    CONSTRAINT FK_UT_Usuario FOREIGN KEY (email) REFERENCES Usuario(email) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE Administrador_Pais_Sede (
    email                VARCHAR(80) NOT NULL,
    paisJurisdiccion     VARCHAR(25) NOT NULL,
    fechaAsignacionCargo DATE        NOT NULL,

    CONSTRAINT PK_Admin PRIMARY KEY (email),
    CONSTRAINT FK_Admin_User FOREIGN KEY (email) REFERENCES Usuario(email) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE Funcionario_Validacion (
    email         VARCHAR(80) NOT NULL,
    numeroLegajo  VARCHAR(25) NOT NULL,

    CONSTRAINT PK_Funcionario PRIMARY KEY (email),
    CONSTRAINT UQ_Legajo UNIQUE (numeroLegajo),
    CONSTRAINT FK_Fun_User FOREIGN KEY (email) REFERENCES Usuario(email) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE Usuario_General (
    email                 VARCHAR(80) NOT NULL,
    fechaRegistro         DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    estadoVerifIdentidad  ENUM('pendiente','verificado','rechazado') NOT NULL DEFAULT 'pendiente',

    CONSTRAINT PK_UsuarioGeneral PRIMARY KEY (email),
    CONSTRAINT FK_UG_User FOREIGN KEY (email) REFERENCES Usuario(email) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE Estadio (
    idEstadio       INT NOT NULL AUTO_INCREMENT,
    nombre          VARCHAR(80) NOT NULL,
    pais            VARCHAR(30) NOT NULL,
    ciudad          VARCHAR(50) NOT NULL,
    emailAdmin      VARCHAR(80) NOT NULL,   -- administrador responsable (1:N)
    fechaAsignacion DATE NOT NULL,          -- cuándo fue asignado el admin

    CONSTRAINT PK_Estadio PRIMARY KEY (idEstadio),
    CONSTRAINT FK_Est_Admin FOREIGN KEY (emailAdmin) REFERENCES Administrador_Pais_Sede(email) ON UPDATE CASCADE
);

CREATE TABLE Sector (
    idSector         INT NOT NULL AUTO_INCREMENT,
    idEstadio        INT NOT NULL,
    codigo           CHAR(1) NOT NULL,
    capacidadMaxima  INT NOT NULL,
    costoEntrada     DECIMAL(10,2) NOT NULL,

    CONSTRAINT PK_Sector_idSector PRIMARY KEY (idSector),
    CONSTRAINT UQ_Sector_idEstadio_codigo UNIQUE (idEstadio, codigo),
    CONSTRAINT FK_Sector_idEstadio_referencias_Estadio FOREIGN KEY (idEstadio) REFERENCES Estadio(idEstadio) ON UPDATE CASCADE,
    CONSTRAINT CHK_Sector_codigo CHECK (codigo IN ('A','B','C','D')),
    CONSTRAINT CHK_Sector_capacidadMaxima CHECK (capacidadMaxima > 0),
    CONSTRAINT CHK_Sector_costoEntrada CHECK (costoEntrada >= 0)
);

CREATE TABLE Equipo (
    idEquipo    INT NOT NULL AUTO_INCREMENT,
    nombre      VARCHAR(60) NOT NULL,
    paisOrigen  VARCHAR(40) NOT NULL,

    CONSTRAINT PK_Equipo PRIMARY KEY (idEquipo),
    CONSTRAINT UQ_Equipo UNIQUE (nombre)
);

CREATE TABLE Evento (
    idEvento      INT NOT NULL AUTO_INCREMENT,
    nombreEvento  VARCHAR(100) NOT NULL,
    fecha         DATE NOT NULL,
    hora          TIME NOT NULL,
    idEstadio     INT NOT NULL,
    emailAdmin    VARCHAR(80) NOT NULL,   -- quien realizó el alta del evento

    CONSTRAINT PK_Evento PRIMARY KEY (idEvento),
    CONSTRAINT FK_Evento_Est FOREIGN KEY (idEstadio) REFERENCES Estadio(idEstadio) ON UPDATE CASCADE,
    CONSTRAINT FK_Evento_Admin FOREIGN KEY (emailAdmin) REFERENCES Administrador_Pais_Sede(email) ON UPDATE CASCADE,
    CONSTRAINT UQ_Evento_Slot UNIQUE (idEstadio, fecha, hora)
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
    idVenta        INT NOT NULL AUTO_INCREMENT,
    numero         VARCHAR(50) NOT NULL,
    fechaVenta     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    estado         ENUM('pendiente','confirmada','paga') NOT NULL DEFAULT 'pendiente',
    montoTotal     DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    emailComprador VARCHAR(80) NOT NULL,

    CONSTRAINT PK_Venta_idVenta PRIMARY KEY (idVenta),
    CONSTRAINT UQ_Venta_numero UNIQUE (numero),
    CONSTRAINT FK_Venta_emailComprador_ref_UsuarioGeneral FOREIGN KEY (emailComprador) REFERENCES Usuario_General(email) ON UPDATE CASCADE
);

CREATE TABLE Entrada (
    idEntrada          INT NOT NULL AUTO_INCREMENT,
    idVenta            INT NOT NULL,
    idEvento           INT NOT NULL,
    idSector           INT NOT NULL,
    emailPropietario   VARCHAR(80) NOT NULL,
    estado             ENUM('activa','consumida','transferencia_pendiente') NOT NULL DEFAULT 'activa',
    cantTransferencias  INT NOT NULL DEFAULT 0,

    CONSTRAINT PK_Entrada_idEntrada PRIMARY KEY (idEntrada),
    CONSTRAINT FK_Entrada_idVenta_ref_Venta FOREIGN KEY (idVenta) REFERENCES Venta(idVenta) ON UPDATE CASCADE,
    CONSTRAINT FK_Entrada_idEvento_idSector_ref_EventoSector FOREIGN KEY (idEvento, idSector) REFERENCES Evento_Sector(idEvento, idSector) ON UPDATE CASCADE,
    CONSTRAINT FK_Entrada_emailPropietario_ref_UsuarioGeneral FOREIGN KEY (emailPropietario) REFERENCES Usuario_General(email) ON UPDATE CASCADE,
    CONSTRAINT CHK_Entrada_cantTransferencias CHECK (cantTransferencias <= 3)
);

CREATE TABLE Transferencia (
    idTransferencia    INT NOT NULL AUTO_INCREMENT,
    idEntrada          INT NOT NULL,
    emailOrigen        VARCHAR(80) NOT NULL,
    emailDestino       VARCHAR(80) NOT NULL,
    fechaTransferencia DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    estado             ENUM('pendiente','aceptada','rechazada') NOT NULL DEFAULT 'pendiente',

    CONSTRAINT PK_Transferencia_idTransferencia PRIMARY KEY (idTransferencia),
    CONSTRAINT FK_Transferencia_idEntrada_ref_Entrada FOREIGN KEY (idEntrada) REFERENCES Entrada(idEntrada) ON UPDATE CASCADE,
    CONSTRAINT FK_Transferencia_emailOrigen_ref_UsuarioGeneral FOREIGN KEY (emailOrigen) REFERENCES Usuario_General(email),
    CONSTRAINT FK_Transferencia_emailDestino_ref_UsuarioGeneral FOREIGN KEY (emailDestino) REFERENCES Usuario_General(email),
    CONSTRAINT CHK_Transferencia_origenDistintoDestino CHECK (emailOrigen <> emailDestino)
);

CREATE TABLE Token_QR (
    idToken             INT NOT NULL AUTO_INCREMENT,
    idEntrada           INT NOT NULL,
    valor               VARCHAR(250) NOT NULL,
    fechaHoraGenerado   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    tiempoVencimiento   INT NOT NULL DEFAULT 30,  -- segundos
    estado              ENUM('activo','expirado','usado') NOT NULL DEFAULT 'activo',

    CONSTRAINT PK_TokenQR_idToken PRIMARY KEY (idToken),
    CONSTRAINT FK_TokenQR_idEntrada_ref_Entrada FOREIGN KEY (idEntrada) REFERENCES Entrada(idEntrada) ON UPDATE CASCADE
);

CREATE TABLE Dispositivo (
    idDispositivo     INT NOT NULL AUTO_INCREMENT,
    dirMAC            VARCHAR(20) NOT NULL,
    emailFuncionario  VARCHAR(80) NOT NULL,

    CONSTRAINT PK_Dispositivo_idDispositivo PRIMARY KEY (idDispositivo),
    CONSTRAINT UQ_Dispositivo_dirMAC UNIQUE (dirMAC),
    CONSTRAINT FK_Dispositivo_emailFuncionario_ref_Funcionario FOREIGN KEY (emailFuncionario) REFERENCES Funcionario_Validacion(email) ON UPDATE CASCADE
);

CREATE TABLE Validacion_Entrada (
    idValidacion         INT NOT NULL AUTO_INCREMENT,
    idEntrada            INT NOT NULL,
    idToken              INT NOT NULL,
    idDispositivo        INT NOT NULL,
    emailFuncionario     VARCHAR(80) NOT NULL,
    fechaHoraValidacion  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT PK_ValEntrada_idValidacion PRIMARY KEY (idValidacion),
    CONSTRAINT UQ_ValidacionAcceso_idEntrada UNIQUE (idEntrada),
    CONSTRAINT FK_ValidacionAcceso_idEntrada_ref_Entrada FOREIGN KEY (idEntrada) REFERENCES Entrada(idEntrada) ON UPDATE CASCADE,
    CONSTRAINT FK_ValidacionAcceso_idToken_ref_TokenQR FOREIGN KEY (idToken) REFERENCES Token_QR(idToken) ON UPDATE CASCADE,
    CONSTRAINT FK_ValidacionAcceso_idDispositivo_ref_Dispositivo FOREIGN KEY (idDispositivo) REFERENCES Dispositivo(idDispositivo) ON UPDATE CASCADE,
    CONSTRAINT FK_ValidacionAcceso_emailFuncionario_referencias_Funcionario FOREIGN KEY (emailFuncionario) REFERENCES Funcionario_Validacion(email) ON UPDATE CASCADE
);

CREATE TABLE Asignacion_Funcionario (
    idEvento         INT NOT NULL,
    idSector         INT NOT NULL,
    emailFuncionario VARCHAR(80) NOT NULL,

    CONSTRAINT PK_FuncAsig PRIMARY KEY (idEvento, idSector, emailFuncionario),
    CONSTRAINT FK_FuncAsig_Evento FOREIGN KEY (idEvento) REFERENCES Evento(idEvento),
    CONSTRAINT FK_FuncAsig_Sector FOREIGN KEY (idSector) REFERENCES Sector(idSector),
    CONSTRAINT FK_FuncAsig_Func FOREIGN KEY (emailFuncionario) REFERENCES Funcionario_Validacion(email)
);

CREATE TABLE Tasa_Comision (
    idTasa      INT NOT NULL AUTO_INCREMENT,
    porcentaje  DECIMAL(5,2) NOT NULL,
    fechaDesde  DATE NOT NULL,
    fechaHasta  DATE NULL,

    CONSTRAINT PK_TasaComision PRIMARY KEY (idTasa)
);