"""
Funciones para la gestión de equipos.
"""

try:
    from .connection import get_db_connection
except ImportError:
    from connection import get_db_connection


def listar_equipos():
    """
    Lista todos los equipos registrados.
    
    Returns:
        Lista de diccionarios con información de equipos
    """
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
