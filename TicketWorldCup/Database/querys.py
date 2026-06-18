import uuid
from collections import defaultdict
from hashlib import sha256

try:
    from .connection import get_db_connection
except ImportError:
    from connection import get_db_connection


def _normalizar_items_venta(items):
    if isinstance(items, dict):
        items = [items]

    agrupados = defaultdict(int)
    for item in items:
        if isinstance(item, dict):
            id_evento = int(item["id_evento"])
            id_sector = str(item["id_sector"])
            cantidad = int(item["cantidad"])
        else:
            id_evento, id_sector, cantidad = item
            id_evento = int(id_evento)
            id_sector = str(id_sector)
            cantidad = int(cantidad)

        if cantidad <= 0:
            raise ValueError("La cantidad debe ser mayor a 0")

        agrupados[(id_evento, id_sector)] += cantidad

    return [
        {"id_evento": id_evento, "id_sector": id_sector, "cantidad": cantidad}
        for (id_evento, id_sector), cantidad in agrupados.items()
    ]


def _obtener_password_hash(datos):
    password = datos.get("passw") or datos.get("password")
    if not password:
        raise ValueError("Falta la contraseña del usuario")
    return sha256(password.encode("utf-8")).hexdigest()


def _obtener_tasa_comision_actual(cursor):
    cursor.execute(
        """
        SELECT porcentaje
        FROM Tasa_Comision
        WHERE fechaDesde <= CURDATE()
          AND (fechaHasta IS NULL OR fechaHasta >= CURDATE())
        ORDER BY fechaDesde DESC, idTasa DESC
        LIMIT 1
        """
    )
    tasa = cursor.fetchone()
    if not tasa:
        return 0.05
    return float(tasa["porcentaje"]) / 100.0


def autenticar_usuario(email, password):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT
                u.email,
                u.passw,
                ug.estadoVerifIdentidad,
                ug.fechaRegistro,
                CASE WHEN ug.email IS NOT NULL THEN 1 ELSE 0 END AS esUsuarioGeneral,
                CASE WHEN a.email IS NOT NULL THEN 1 ELSE 0 END AS esAdministrador,
                CASE WHEN f.email IS NOT NULL THEN 1 ELSE 0 END AS esFuncionario
            FROM Usuario u
            LEFT JOIN Usuario_General ug ON ug.email = u.email
            LEFT JOIN Administrador_Pais_Sede a ON a.email = u.email
            LEFT JOIN Funcionario_Validacion f ON f.email = u.email
            WHERE u.email = %s
              AND u.passw = %s
            LIMIT 1
            """,
            (email, sha256(password.encode("utf-8")).hexdigest()),
        )
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


def registrar_usuario_general(datos, telefonos):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        conn.start_transaction()

        cursor.execute(
            """
            INSERT INTO Usuario (
                email, docPais, docTipo, docNumero,
                dirPais, dirLocalidad, dirCalle, dirNumero, dirCodigoPostal, passw
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                datos["email"],
                datos["docPais"],
                datos["docTipo"],
                datos["docNumero"],
                datos["dirPais"],
                datos["dirLocalidad"],
                datos["dirCalle"],
                datos["dirNumero"],
                datos["dirCodigoPostal"],
                _obtener_password_hash(datos),
            ),
        )

        cursor.execute(
            "INSERT INTO Usuario_General (email, estadoVerifIdentidad) VALUES (%s, 'pendiente')",
            (datos["email"],),
        )

        for telefono in telefonos:
            cursor.execute(
                "INSERT INTO Usuario_Telefono (email, telefono) VALUES (%s, %s)",
                (datos["email"], telefono),
            )

        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"Error en registro: {e}")
        return False
    finally:
        cursor.close()
        conn.close()


def registrar_usuario_admin(datos, pais_jurisdiccion, fecha_asignacion_cargo):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        conn.start_transaction()

        cursor.execute(
            """
            INSERT INTO Usuario (
                email, docPais, docTipo, docNumero,
                dirPais, dirLocalidad, dirCalle, dirNumero, dirCodigoPostal, passw
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                datos["email"],
                datos["docPais"],
                datos["docTipo"],
                datos["docNumero"],
                datos["dirPais"],
                datos["dirLocalidad"],
                datos["dirCalle"],
                datos["dirNumero"],
                datos["dirCodigoPostal"],
                _obtener_password_hash(datos),
            ),
        )

        cursor.execute(
            """
            INSERT INTO Administrador_Pais_Sede (email, paisJurisdiccion, fechaAsignacionCargo)
            VALUES (%s, %s, %s)
            """,
            (datos["email"], pais_jurisdiccion, fecha_asignacion_cargo),
        )

        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"Error registrando administrador: {e}")
        return False
    finally:
        cursor.close()
        conn.close()


def registrar_funcionario_validacion(datos, numero_legajo):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        conn.start_transaction()

        cursor.execute(
            """
            INSERT INTO Usuario (
                email, docPais, docTipo, docNumero,
                dirPais, dirLocalidad, dirCalle, dirNumero, dirCodigoPostal, passw
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                datos["email"],
                datos["docPais"],
                datos["docTipo"],
                datos["docNumero"],
                datos["dirPais"],
                datos["dirLocalidad"],
                datos["dirCalle"],
                datos["dirNumero"],
                datos["dirCodigoPostal"],
                _obtener_password_hash(datos),
            ),
        )

        cursor.execute(
            "INSERT INTO Funcionario_Validacion (email, numeroLegajo) VALUES (%s, %s)",
            (datos["email"], numero_legajo),
        )

        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"Error registrando funcionario: {e}")
        return False
    finally:
        cursor.close()
        conn.close()


def crear_estadio(nombre, pais, ciudad, email_admin, fecha_asignacion):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO Estadio (nombre, pais, ciudad, emailAdmin, fechaAsignacion)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (nombre, pais, ciudad, email_admin, fecha_asignacion),
        )
        conn.commit()
        return cursor.lastrowid
    except Exception as e:
        conn.rollback()
        print(f"Error creando estadio: {e}")
        return False
    finally:
        cursor.close()
        conn.close()


def crear_sector(id_estadio, codigo, capacidad_maxima, costo_entrada):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO Sector (idEstadio, codigo, capacidadMaxima, costoEntrada)
            VALUES (%s, %s, %s, %s)
            """,
            (id_estadio, codigo, capacidad_maxima, costo_entrada),
        )
        conn.commit()
        return cursor.lastrowid
    except Exception as e:
        conn.rollback()
        print(f"Error creando sector: {e}")
        return False
    finally:
        cursor.close()
        conn.close()


def listar_estadios():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT
                idEstadio,
                nombre,
                pais,
                ciudad,
                emailAdmin,
                fechaAsignacion
            FROM Estadio
            ORDER BY nombre
            """
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def listar_equipos():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT
                idEquipo,
                nombre,
                paisOrigen
            FROM Equipo
            ORDER BY nombre
            """
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def listar_codigos_sector_disponibles(id_estadio):
    codigos = ['A', 'B', 'C', 'D']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT codigo FROM Sector WHERE idEstadio = %s",
            (id_estadio,),
        )
        usados = {fila['codigo'] for fila in cursor.fetchall()}
        return [{'codigo': codigo} for codigo in codigos if codigo not in usados]
    finally:
        cursor.close()
        conn.close()


def listar_equipos_disponibles_evento(id_evento):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT
                eq.idEquipo,
                eq.nombre,
                eq.paisOrigen
            FROM Equipo eq
            WHERE eq.idEquipo NOT IN (
                SELECT ee.idEquipo
                FROM Evento_Equipo ee
                WHERE ee.idEvento = %s
            )
            ORDER BY eq.nombre
            """,
            (id_evento,),
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def listar_sectores_disponibles_evento(id_evento):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT
                s.idSector,
                s.codigo,
                s.capacidadMaxima,
                s.costoEntrada,
                st.nombre AS estadio
            FROM Evento e
            JOIN Estadio st ON st.idEstadio = e.idEstadio
            JOIN Sector s ON s.idEstadio = st.idEstadio
            WHERE e.idEvento = %s
              AND s.idSector NOT IN (
                  SELECT es.idSector
                  FROM Evento_Sector es
                  WHERE es.idEvento = %s
              )
            ORDER BY s.codigo
            """,
            (id_evento, id_evento),
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def listar_sectores():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT
                s.idSector,
                s.idEstadio,
                e.nombre AS estadio,
                s.codigo,
                s.capacidadMaxima,
                s.costoEntrada
            FROM Sector s
            JOIN Estadio e ON e.idEstadio = s.idEstadio
            ORDER BY e.nombre, s.codigo
            """
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def registrar_dispositivo(dir_mac, email_funcionario):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO Dispositivo (dirMAC, emailFuncionario) VALUES (%s, %s)",
            (dir_mac, email_funcionario),
        )
        conn.commit()
        return cursor.lastrowid
    except Exception as e:
        conn.rollback()
        print(f"Error registrando dispositivo: {e}")
        return False
    finally:
        cursor.close()
        conn.close()


def crear_evento(nombre_evento, fecha, hora, id_estadio, email_admin):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO Evento (nombreEvento, fecha, hora, idEstadio, emailAdmin)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (nombre_evento, fecha, hora, id_estadio, email_admin),
        )
        conn.commit()
        return cursor.lastrowid
    except Exception as e:
        conn.rollback()
        print(f"Error creando evento: {e}")
        return False
    finally:
        cursor.close()
        conn.close()


def vincular_equipo_evento(id_evento, id_equipo, rol):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO Evento_Equipo (idEvento, idEquipo, rol) VALUES (%s, %s, %s)",
            (id_evento, id_equipo, rol),
        )
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"Error vinculando equipo al evento: {e}")
        return False
    finally:
        cursor.close()
        conn.close()


def habilitar_sector_evento(id_evento, id_sector):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO Evento_Sector (idEvento, idSector) VALUES (%s, %s)",
            (id_evento, id_sector),
        )
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"Error habilitando sector del evento: {e}")
        return False
    finally:
        cursor.close()
        conn.close()


def listar_eventos():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT
                e.idEvento,
                e.nombreEvento,
                e.fecha,
                e.hora,
                e.idEstadio,
                s.nombre AS estadio,
                s.pais AS paisEstadio,
                s.ciudad AS ciudadEstadio,
                GROUP_CONCAT(DISTINCT CONCAT(eq.nombre, ' (', ee.rol, ')') ORDER BY ee.rol SEPARATOR ', ') AS equipos
            FROM Evento e
            JOIN Estadio s ON s.idEstadio = e.idEstadio
            LEFT JOIN Evento_Equipo ee ON ee.idEvento = e.idEvento
            LEFT JOIN Equipo eq ON eq.idEquipo = ee.idEquipo
            GROUP BY e.idEvento, e.nombreEvento, e.fecha, e.hora, e.idEstadio, s.nombre, s.pais, s.ciudad
            ORDER BY e.fecha, e.hora
            """
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def listar_compradores():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT
                u.email,
                ug.estadoVerifIdentidad,
                ug.fechaRegistro
            FROM Usuario_General ug
            JOIN Usuario u ON u.email = ug.email
            ORDER BY u.email
            """
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def listar_vinculaciones():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT
                'equipo' AS tipo,
                ee.idEvento,
                ev.nombreEvento,
                ee.idEquipo AS idReferencia,
                eq.nombre AS referencia,
                ee.rol AS detalle
            FROM Evento_Equipo ee
            JOIN Evento ev ON ev.idEvento = ee.idEvento
            JOIN Equipo eq ON eq.idEquipo = ee.idEquipo
            UNION ALL
            SELECT
                'sector' AS tipo,
                es.idEvento,
                ev.nombreEvento,
                es.idSector AS idReferencia,
                s.codigo AS referencia,
                CONCAT('habilitado en ', st.nombre) AS detalle
            FROM Evento_Sector es
            JOIN Evento ev ON ev.idEvento = es.idEvento
            JOIN Sector s ON s.idSector = es.idSector
            JOIN Estadio st ON st.idEstadio = ev.idEstadio
            ORDER BY idEvento, tipo, idReferencia
            """
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def listar_sectores_evento(id_evento):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT
                s.idSector,
                s.codigo,
                s.idEstadio,
                e.nombreEvento AS evento,
                s.capacidadMaxima,
                s.costoEntrada,
                COUNT(en.idEntrada) AS entradasVendidas,
                (s.capacidadMaxima - COUNT(en.idEntrada)) AS entradasDisponibles
            FROM Evento_Sector es
            JOIN Evento e ON e.idEvento = es.idEvento
            JOIN Sector s ON s.idEstadio = e.idEstadio AND s.idSector = es.idSector
            LEFT JOIN Entrada en ON en.idEvento = es.idEvento AND en.idSector = es.idSector
            WHERE es.idEvento = %s
            GROUP BY s.idSector, s.codigo, s.idEstadio, e.nombreEvento, s.capacidadMaxima, s.costoEntrada
            ORDER BY s.codigo
            """,
            (id_evento,),
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def registrar_venta_y_entradas(email_comprador, items, estado='paga'):
    items_normalizados = _normalizar_items_venta(items)
    total_entradas = sum(item["cantidad"] for item in items_normalizados)

    if total_entradas <= 0 or total_entradas > 5:
        return False

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        conn.start_transaction()

        detalle_compra = []
        monto_base = 0

        for item in items_normalizados:
            cursor.execute(
                """
                SELECT
                    s.costoEntrada,
                    s.capacidadMaxima
                FROM Evento_Sector es
                JOIN Evento e ON e.idEvento = es.idEvento
                JOIN Sector s ON s.idEstadio = e.idEstadio AND s.idSector = es.idSector
                WHERE es.idEvento = %s AND es.idSector = %s
                FOR UPDATE
                """,
                (item["id_evento"], item["id_sector"]),
            )
            sector = cursor.fetchone()
            if not sector:
                conn.rollback()
                return False

            cursor.execute(
                "SELECT COUNT(*) AS total FROM Entrada WHERE idEvento = %s AND idSector = %s",
                (item["id_evento"], item["id_sector"]),
            )
            vendidas = cursor.fetchone()["total"]

            if vendidas + item["cantidad"] > sector["capacidadMaxima"]:
                conn.rollback()
                return False

            monto_base += float(sector["costoEntrada"]) * item["cantidad"]
            detalle_compra.append(item)

        tasa_comision = _obtener_tasa_comision_actual(cursor)
        monto_total = round(monto_base * (1 + tasa_comision), 2)
        numero_venta = f"VTA-{uuid.uuid4().hex[:12].upper()}"

        cursor.execute(
            """
            INSERT INTO Venta (numero, estado, montoTotal, emailComprador)
            VALUES (%s, %s, %s, %s)
            """,
            (numero_venta, estado, monto_total, email_comprador),
        )
        id_venta = cursor.lastrowid

        for item in detalle_compra:
            for _ in range(item["cantidad"]):
                cursor.execute(
                    """
                    INSERT INTO Entrada (
                        idVenta, idEvento, idSector, emailPropietario, estado, cantTransferencias
                    ) VALUES (%s, %s, %s, %s, 'activa', 0)
                    """,
                    (id_venta, item["id_evento"], item["id_sector"], email_comprador),
                )

        conn.commit()
        return id_venta
    except Exception as e:
        conn.rollback()
        print(f"Error en venta: {e}")
        return False
    finally:
        cursor.close()
        conn.close()


def ejecutar_transaccion_venta(email, id_evento, id_sector, cantidad):
    return bool(
        registrar_venta_y_entradas(
            email,
            [{"id_evento": id_evento, "id_sector": id_sector, "cantidad": cantidad}],
        )
    )


def listar_compras_usuario(email_comprador):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT
                v.idVenta,
                v.numero,
                v.fechaVenta,
                v.estado,
                v.montoTotal,
                COUNT(e.idEntrada) AS cantidadEntradas
            FROM Venta v
            LEFT JOIN Entrada e ON e.idVenta = v.idVenta
            WHERE v.emailComprador = %s
            GROUP BY v.idVenta, v.numero, v.fechaVenta, v.estado, v.montoTotal
            ORDER BY v.fechaVenta DESC
            """,
            (email_comprador,),
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def listar_entradas_usuario(email_propietario):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT
                en.idEntrada,
                en.estado,
                en.cantTransferencias,
                en.emailPropietario,
                en.idSector,
                ev.idEvento,
                ev.nombreEvento,
                ev.fecha,
                ev.hora,
                s.nombre AS estadio,
                s.ciudad,
                v.numero AS numeroVenta,
                v.fechaVenta
            FROM Entrada en
            JOIN Venta v ON v.idVenta = en.idVenta
            JOIN Evento ev ON ev.idEvento = en.idEvento
            JOIN Estadio s ON s.idEstadio = ev.idEstadio
            WHERE en.emailPropietario = %s
            ORDER BY ev.fecha, ev.hora, en.idEntrada
            """,
            (email_propietario,),
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def listar_transferencias_usuario(email_usuario):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT
                t.idTransferencia,
                t.idEntrada,
                t.emailOrigen,
                t.emailDestino,
                t.fechaTransferencia,
                t.estado,
                en.idEvento,
                en.idSector
            FROM Transferencia t
            JOIN Entrada en ON en.idEntrada = t.idEntrada
            WHERE t.emailOrigen = %s OR t.emailDestino = %s
            ORDER BY t.fechaTransferencia DESC
            """,
            (email_usuario, email_usuario),
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def solicitar_transferencia(id_entrada, email_origen, email_destino):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        conn.start_transaction()

        cursor.execute(
            """
            SELECT idEntrada, emailPropietario, estado, cantTransferencias
            FROM Entrada
            WHERE idEntrada = %s
            FOR UPDATE
            """,
            (id_entrada,),
        )
        entrada = cursor.fetchone()
        if not entrada:
            conn.rollback()
            return False

        if entrada["emailPropietario"] != email_origen:
            conn.rollback()
            return False

        if entrada["estado"] == "consumida" or entrada["cantTransferencias"] >= 3:
            conn.rollback()
            return False

        cursor.execute(
            """
            INSERT INTO Transferencia (idEntrada, emailOrigen, emailDestino, estado)
            VALUES (%s, %s, %s, 'pendiente')
            """,
            (id_entrada, email_origen, email_destino),
        )
        cursor.execute(
            "UPDATE Entrada SET estado = 'transferencia_pendiente' WHERE idEntrada = %s",
            (id_entrada,),
        )

        conn.commit()
        return cursor.lastrowid
    except Exception as e:
        conn.rollback()
        print(f"Error solicitando transferencia: {e}")
        return False
    finally:
        cursor.close()
        conn.close()


def responder_transferencia(id_transferencia, estado):
    if estado not in ("aceptada", "rechazada"):
        return False

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        conn.start_transaction()

        cursor.execute(
            """
            SELECT idTransferencia, idEntrada, emailOrigen, emailDestino, estado
            FROM Transferencia
            WHERE idTransferencia = %s
            FOR UPDATE
            """,
            (id_transferencia,),
        )
        transferencia = cursor.fetchone()
        if not transferencia or transferencia["estado"] != "pendiente":
            conn.rollback()
            return False

        if estado == "aceptada":
            cursor.execute(
                """
                SELECT estado, cantTransferencias, emailPropietario
                FROM Entrada
                WHERE idEntrada = %s
                FOR UPDATE
                """,
                (transferencia["idEntrada"],),
            )
            entrada = cursor.fetchone()
            if not entrada or entrada["estado"] == "consumida" or entrada["cantTransferencias"] >= 3:
                conn.rollback()
                return False

            cursor.execute(
                """
                UPDATE Entrada
                SET emailPropietario = %s,
                    cantTransferencias = cantTransferencias + 1,
                    estado = 'activa'
                WHERE idEntrada = %s
                """,
                (transferencia["emailDestino"], transferencia["idEntrada"]),
            )
        else:
            cursor.execute(
                """
                UPDATE Entrada
                SET estado = 'activa'
                WHERE idEntrada = %s AND estado = 'transferencia_pendiente'
                """,
                (transferencia["idEntrada"],),
            )

        cursor.execute(
            "UPDATE Transferencia SET estado = %s WHERE idTransferencia = %s",
            (estado, id_transferencia),
        )

        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"Error respondiendo transferencia: {e}")
        return False
    finally:
        cursor.close()
        conn.close()


def registrar_token_qr(id_entrada, valor=None, tiempo_vencimiento=30):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        conn.start_transaction()

        cursor.execute(
            "UPDATE Token_QR SET estado = 'expirado' WHERE idEntrada = %s AND estado = 'activo'",
            (id_entrada,),
        )

        if valor is None:
            valor = f"QR-{uuid.uuid4().hex.upper()}"

        cursor.execute(
            """
            INSERT INTO Token_QR (idEntrada, valor, fechaHoraGenerado, tiempoVencimiento, estado)
            VALUES (%s, %s, CURRENT_TIMESTAMP, %s, 'activo')
            """,
            (id_entrada, valor, tiempo_vencimiento),
        )
        conn.commit()
        return cursor.lastrowid
    except Exception as e:
        conn.rollback()
        print(f"Error registrando token QR: {e}")
        return False
    finally:
        cursor.close()
        conn.close()


def obtener_token_activo(id_entrada):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT idToken, idEntrada, valor, fechaHoraGenerado, tiempoVencimiento, estado
            FROM Token_QR
            WHERE idEntrada = %s
              AND estado = 'activo'
              AND TIMESTAMPDIFF(SECOND, fechaHoraGenerado, NOW()) <= tiempoVencimiento
            ORDER BY fechaHoraGenerado DESC
            LIMIT 1
            """,
            (id_entrada,),
        )
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


def validar_entrada(id_token, id_dispositivo, email_funcionario):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        conn.start_transaction()

        cursor.execute(
            """
            SELECT
                t.idToken,
                t.idEntrada,
                t.valor,
                t.fechaHoraGenerado,
                t.tiempoVencimiento,
                t.estado AS estadoToken,
                e.estado AS estadoEntrada,
                e.emailPropietario
            FROM Token_QR t
            JOIN Entrada e ON e.idEntrada = t.idEntrada
            WHERE t.idToken = %s
            FOR UPDATE
            """,
            (id_token,),
        )
        token = cursor.fetchone()
        if not token:
            conn.rollback()
            return False

        if token["estadoToken"] != "activo":
            conn.rollback()
            return False

        cursor.execute(
            """
            SELECT 1
            FROM Dispositivo
            WHERE idDispositivo = %s AND emailFuncionario = %s
            """,
            (id_dispositivo, email_funcionario),
        )
        if cursor.fetchone() is None:
            conn.rollback()
            return False

        cursor.execute(
            """
            INSERT INTO Validacion_Entrada (
                idEntrada, idToken, idDispositivo, emailFuncionario, fechaHoraValidacion
            ) VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)
            """,
            (token["idEntrada"], id_token, id_dispositivo, email_funcionario),
        )

        cursor.execute(
            "UPDATE Entrada SET estado = 'consumida' WHERE idEntrada = %s",
            (token["idEntrada"],),
        )
        cursor.execute(
            "UPDATE Token_QR SET estado = 'usado' WHERE idToken = %s",
            (id_token,),
        )

        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"Error validando entrada: {e}")
        return False
    finally:
        cursor.close()
        conn.close()


def ranking_eventos_mas_vendidos(limite=10):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT
                ev.idEvento,
                ev.nombreEvento,
                ev.fecha,
                ev.hora,
                COUNT(en.idEntrada) AS entradasVendidas,
                COALESCE(SUM(v.montoTotal), 0) AS facturacion
            FROM Evento ev
            LEFT JOIN Entrada en ON en.idEvento = ev.idEvento
            LEFT JOIN Venta v ON v.idVenta = en.idVenta
            GROUP BY ev.idEvento, ev.nombreEvento, ev.fecha, ev.hora
            ORDER BY entradasVendidas DESC, ev.fecha ASC, ev.hora ASC
            LIMIT %s
            """,
            (limite,),
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def ranking_mayores_compradores(limite=10):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT
                v.emailComprador,
                COUNT(en.idEntrada) AS totalEntradas,
                COUNT(DISTINCT v.idVenta) AS totalCompras,
                COALESCE(SUM(v.montoTotal), 0) AS totalGastado
            FROM Venta v
            LEFT JOIN Entrada en ON en.idVenta = v.idVenta
            GROUP BY v.emailComprador
            ORDER BY totalEntradas DESC, totalGastado DESC
            LIMIT %s
            """,
            (limite,),
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def cobertura_funcionario_evento(id_evento, email_funcionario):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT
                af.idSector,
                s.codigo,
                COUNT(DISTINCT ve.idValidacion) AS validaciones
            FROM Asignacion_Funcionario af
            JOIN Sector s ON s.idSector = af.idSector
            LEFT JOIN Entrada en ON en.idEvento = af.idEvento AND en.idSector = af.idSector
            LEFT JOIN Validacion_Entrada ve ON ve.idEntrada = en.idEntrada AND ve.emailFuncionario = af.emailFuncionario
            WHERE af.idEvento = %s AND af.emailFuncionario = %s
            GROUP BY af.idSector, s.codigo
            ORDER BY s.codigo
            """,
            (id_evento, email_funcionario),
        )
        resultado = cursor.fetchall()
        for fila in resultado:
            fila["cumple"] = fila["validaciones"] > 0
        return resultado
    finally:
        cursor.close()
        conn.close()
def registrar_usuario_general(datos, telefonos):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        conn.start_transaction()
        
        # 1. Insertar en Usuario
        sql_user = """INSERT INTO Usuario (email, docPais, docTipo, docNumero, dirPais, dirLocalidad, dirCalle, dirNumero, dirCodigoPostal) 
                      VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        cursor.execute(sql_user, (datos['email'], datos['docPais'], datos['docTipo'], datos['docNumero'], datos['dirPais'], datos['dirLocalidad'], datos['dirCalle'], datos['dirNumero'], datos['dirCodigoPostal']))
        
        # 2. Insertar en Usuario_General
        sql_gen = "INSERT INTO Usuario_General (email, estadoVerifIdentidad) VALUES (%s, 'pendiente')"
        cursor.execute(sql_gen, (datos['email'],))
        
        # 3. Insertar Teléfonos (si existen)
        for tel in telefonos:
            cursor.execute("INSERT INTO Usuario_Telefono (email, telefono) VALUES (%s, %s)", (datos['email'], tel))
            
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"Error en registro: {e}")
        return False
    finally:
        cursor.close()
        conn.close()


def ejecutar_transaccion_venta(email, id_evento, id_sector, cantidad):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        conn.start_transaction()
        
        # 1. Verificar Capacidad Máxima del Sector bloqueando la fila para concurrencia (FOR UPDATE)
        cursor.execute("""
            SELECT s.capacidadMaxima, s.costoEntrada 
            FROM Sector s
            JOIN Evento e ON e.idEstadio = s.idEstadio
            WHERE e.idEvento = %s AND s.codigo = %s FOR UPDATE
        """, (id_evento, id_sector))
        sector_info = cursor.fetchone()
        
        # Contar cuántas entradas ya se vendieron para este evento y sector
        cursor.execute("SELECT COUNT(*) AS total FROM Entrada WHERE idEvento = %s AND idSector = %s", (id_evento, id_sector))
        vendidas = cursor.fetchone()['total']
        
        if vendidas + cantidad > sector_info['capacidadMaxima']:
            conn.rollback() # Sobre-aforo detectado
            return False
            
        # 2. Calcular montos (Costo + 5% comisión)
        subtotal = sector_info['costoEntrada'] * cantidad
        monto_total = subtotal * 1.05
        
        # 3. Crear el registro en Venta
        num_venta = f"VTA-{id_evento}-{email[:3].upper()}"
        cursor.execute("""
            INSERT INTO Venta (numero, estado, montoTotal, emailComprador) 
            VALUES (%s, 'paga', %s, %s)
        """, (num_venta, monto_total, email))
        id_venta = cursor.lastrowid
        
        # 4. Crear las entradas individuales
        for _ in range(cantidad):
            cursor.execute("""
                INSERT INTO Entrada (idVenta, idEvento, idSector, emailPropietario, estado, cantTransferencias)
                VALUES (%s, %s, %s, %s, 'activa', 0)
            """, (id_venta, id_evento, id_sector, email))
            
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()