"""
Funciones para la gestión de infraestructura: estadios y sectores.
"""

try:
    from .connection import get_db_connection
    from .utils import interpretar_error_db
except ImportError:
    from connection import get_db_connection
    from utils import interpretar_error_db


# ============================================================================
# ESTADIOS
# ============================================================================

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
        return cursor.lastrowid, None
    except Exception as e:
        conn.rollback()
        err = _interpretar_error_db(e, "estadio")
        return False, err
    finally:
        cursor.close()
        conn.close()


def listar_estadios():
    """
    Lista todos los estadios registrados.
    
    Returns:
        Lista de diccionarios con información de estadios
    """
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


# ============================================================================
# SECTORES
# ============================================================================

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
        return cursor.lastrowid, None
    except Exception as e:
        conn.rollback()
        err = interpretar_error_db(e, "sector")
        return False, err
    finally:
        cursor.close()
        conn.close()


def listar_sectores():
    """
    Lista todos los sectores de todos los estadios.
    
    Returns:
        Lista de diccionarios con información de sectores
    """
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


def listar_codigos_sector_disponibles(id_estadio):
    """
    Lista los códigos de sector aún disponibles en un estadio.
    
    Args:
        id_estadio: ID del estadio
        
    Returns:
        Lista de diccionarios con códigos disponibles (A, B, C, D)
    """
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
