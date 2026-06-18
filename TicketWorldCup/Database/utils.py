"""
Funciones utilitarias y helpers para las operaciones de base de datos.
"""

from collections import defaultdict
from hashlib import sha256

try:
    from .connection import get_db_connection
except ImportError:
    from connection import get_db_connection


def normalizar_items_venta(items):
    """
    Normaliza los items de venta, agrupando por evento y sector.
    
    Args:
        items: Lista de diccionarios o tuplas con id_evento, id_sector, cantidad
        
    Returns:
        Lista normalizada de items
    """
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


def obtener_password_hash(datos):
    """
    Obtiene el hash SHA-256 de la contraseña del usuario.
    
    Args:
        datos: Diccionario con 'passw' o 'password'
        
    Returns:
        Hash SHA-256 de la contraseña
    """
    password = datos.get("passw") or datos.get("password")
    if not password:
        raise ValueError("Falta la contraseña del usuario")
    return sha256(password.encode("utf-8")).hexdigest()


def obtener_tasa_comision_actual(cursor):
    """
    Obtiene la tasa de comisión vigente de la tabla Tasa_Comision.
    
    Args:
        cursor: Cursor de la base de datos
        
    Returns:
        Porcentaje de comisión como decimal (ej: 0.05 para 5%)
    """
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
