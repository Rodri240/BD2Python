"""
Funciones para la gestión de infraestructura: estadios y sectores.
"""

try:
    from .connection import get_db_connection
except ImportError:
    from connection import get_db_connection


# ============================================================================
# ESTADIOS
# ============================================================================

def crear_estadio(nombre, pais, ciudad, email_admin, fecha_asignacion):
    """
    Crea un nuevo estadio en la base de datos.
    
    Args:
        nombre: Nombre del estadio
        pais: País donde se ubica
        ciudad: Ciudad del estadio
        email_admin: Email del administrador responsable
        fecha_asignacion: Fecha de asignación al administrador
        
    Returns:
        ID del estadio creado, o False si hay error
    """
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
    """
    Crea un nuevo sector dentro de un estadio.
    
    Args:
        id_estadio: ID del estadio propietario
        codigo: Código del sector (A, B, C, D)
        capacidad_maxima: Cantidad máxima de entradas para este sector
        costo_entrada: Precio de entrada por persona
        
    Returns:
        ID del sector creado, o False si hay error
    """
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
