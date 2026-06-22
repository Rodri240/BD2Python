"""
Funciones para la gestión de eventos y vinculaciones.
"""

try:
    from .connection import get_db_connection
    from .utils import interpretar_error_db
except ImportError:
    from connection import get_db_connection
    from utils import interpretar_error_db


def crear_evento(nombre_evento, fecha, hora, id_estadio, email_admin):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # Verificar solapamiento: no puede haber otro evento en el mismo estadio
        # en la misma fecha con menos de 4 horas de diferencia (duración estimada de un partido)
        cursor.execute(
            """
            SELECT idEvento, nombreEvento, TIME_FORMAT(hora, '%H:%i') AS hora
            FROM Evento
            WHERE idEstadio = %s
              AND fecha = %s
              AND hora BETWEEN SUBTIME(%s, '04:00') AND ADDTIME(%s, '04:00')
            LIMIT 1
            """,
            (id_estadio, fecha, hora),
        )
        conflicto = cursor.fetchone()
        if conflicto:
            hora_conflicto = conflicto["hora"]
            return False, (
                f"El estadio ya tiene el evento '{conflicto['nombreEvento']}' "
                f"a las {hora_conflicto} en esa fecha. "
                f"Debe haber al menos 4 horas de diferencia entre eventos en el mismo recinto."
            )

        cursor.close()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO Evento (nombreEvento, fecha, hora, idEstadio, emailAdmin)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (nombre_evento, fecha, hora, id_estadio, email_admin),
        )
        conn.commit()
        return cursor.lastrowid, None
    except Exception as e:
        conn.rollback()
        err = interpretar_error_db(e, "evento")
        return False, err
    finally:
        cursor.close()
        conn.close()


def vincular_equipo_evento(id_evento, id_equipo, rol):
    """
    Vincula un equipo a un evento con un rol específico (local, visitante).
    
    Args:
        id_evento: ID del evento
        id_equipo: ID del equipo
        rol: Rol del equipo ('local' o 'visitante')
        
    Returns:
        True si se vinculó exitosamente, False si hay error
    """
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
    """
    Habilita un sector para un evento (permite vender entradas de ese sector).
    
    Args:
        id_evento: ID del evento
        id_sector: ID del sector a habilitar
        
    Returns:
        True si se habilitó exitosamente, False si hay error
    """
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


def listar_eventos(email_admin=None):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        where = "WHERE e.emailAdmin = %s" if email_admin else ""
        params = (email_admin,) if email_admin else ()
        cursor.execute(
            f"""
            SELECT
                e.idEvento,
                e.nombreEvento,
                e.fecha,
                TIME_FORMAT(e.hora, '%H:%i') AS hora,
                e.idEstadio,
                s.nombre AS estadio,
                s.pais AS paisEstadio,
                s.ciudad AS ciudadEstadio,
                GROUP_CONCAT(DISTINCT CONCAT(eq.nombre, ' (', ee.rol, ')') ORDER BY ee.rol SEPARATOR ', ') AS equipos
            FROM Evento e
            JOIN Estadio s ON s.idEstadio = e.idEstadio
            LEFT JOIN Evento_Equipo ee ON ee.idEvento = e.idEvento
            LEFT JOIN Equipo eq ON eq.idEquipo = ee.idEquipo
            {where}
            GROUP BY e.idEvento, e.nombreEvento, e.fecha, e.hora, e.idEstadio, s.nombre, s.pais, s.ciudad
            ORDER BY e.fecha, e.hora
            """,
            params,
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def listar_vinculaciones():
    """
    Lista todas las vinculaciones de equipos y sectores a eventos.
    
    Returns:
        Lista de diccionarios con información de vinculaciones
    """
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


def listar_equipos_disponibles_evento(id_evento):
    """
    Lista los equipos que NO están vinculados a un evento específico.
    
    Args:
        id_evento: ID del evento
        
    Returns:
        Lista de diccionarios con equipos disponibles
    """
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
            WHERE NOT EXISTS (
                SELECT 1
                FROM Evento_Equipo ee
                WHERE ee.idEvento = %s AND ee.idEquipo = eq.idEquipo
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
    """
    Lista los sectores que NO están habilitados en un evento específico.
    
    Args:
        id_evento: ID del evento
        
    Returns:
        Lista de diccionarios con sectores disponibles
    """
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
              AND NOT EXISTS (
                  SELECT 1
                  FROM Evento_Sector es
                  WHERE es.idEvento = %s AND es.idSector = s.idSector
              )
            ORDER BY s.codigo
            """,
            (id_evento, id_evento),
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def listar_sectores_evento(id_evento):
    """
    Lista los sectores habilitados en un evento con información de disponibilidad.
    
    Args:
        id_evento: ID del evento
        
    Returns:
        Lista de diccionarios con sectores y disponibilidad
    """
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


def listar_entradas_no_validadas_por_evento(id_evento, email_funcionario=None):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        if email_funcionario:
            cursor.execute(
                """
                SELECT e.idEntrada, e.emailPropietario, e.idSector, s.codigo AS sectorCodigo,
                       e.estado, e.cantTransferencias
                FROM Entrada e
                JOIN Sector s ON s.idSector = e.idSector
                JOIN Asignacion_Funcionario af
                    ON af.idEvento = e.idEvento
                    AND af.idSector = e.idSector
                    AND af.emailFuncionario = %s
                WHERE e.idEvento = %s
                  AND e.estado != 'consumida'
                  AND NOT EXISTS (
                      SELECT 1 FROM Validacion_Entrada ve WHERE ve.idEntrada = e.idEntrada
                  )
                ORDER BY s.codigo, e.emailPropietario
                """,
                (email_funcionario, id_evento),
            )
        else:
            cursor.execute(
                """
                SELECT e.idEntrada, e.emailPropietario, e.idSector, s.codigo AS sectorCodigo,
                       e.estado, e.cantTransferencias
                FROM Entrada e
                JOIN Sector s ON s.idSector = e.idSector
                WHERE e.idEvento = %s
                  AND e.estado != 'consumida'
                  AND NOT EXISTS (
                      SELECT 1 FROM Validacion_Entrada ve WHERE ve.idEntrada = e.idEntrada
                  )
                ORDER BY s.codigo, e.emailPropietario
                """,
                (id_evento,),
            )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def listar_entradas_validadas_por_evento(id_evento):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT e.idEntrada, e.emailPropietario, s.codigo AS sectorCodigo,
                   ve.fechaHoraValidacion, ve.emailFuncionario, d.dirMAC
            FROM Entrada e
            JOIN Sector s ON s.idSector = e.idSector
            JOIN Validacion_Entrada ve ON ve.idEntrada = e.idEntrada
            JOIN Dispositivo d ON d.idDispositivo = ve.idDispositivo
            WHERE e.idEvento = %s
            ORDER BY ve.fechaHoraValidacion DESC
            """,
            (id_evento,),
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()
