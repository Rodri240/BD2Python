"""
Funciones para la gestión de eventos y vinculaciones.
"""

try:
    from .connection import get_db_connection
except ImportError:
    from connection import get_db_connection


def crear_evento(nombre_evento, fecha, hora, id_estadio, email_admin):
    """
    Crea un nuevo evento en un estadio.
    
    Args:
        nombre_evento: Nombre del evento
        fecha: Fecha del evento (YYYY-MM-DD)
        hora: Hora del evento (HH:MM:SS)
        id_estadio: ID del estadio donde se realiza
        email_admin: Email del administrador responsable
        
    Returns:
        ID del evento creado, o False si hay error
    """
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


def listar_eventos():
    """
    Lista todos los eventos registrados con sus detalles.
    
    Returns:
        Lista de diccionarios con información de eventos
    """
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
