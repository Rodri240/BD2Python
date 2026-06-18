"""
Funciones para la gestión de dispositivos de validación.
"""

try:
    from .connection import get_db_connection
except ImportError:
    from connection import get_db_connection


def registrar_dispositivo(dir_mac, email_funcionario):
    """
    Registra un nuevo dispositivo de validación asociado a un funcionario.
    
    Args:
        dir_mac: Dirección MAC del dispositivo
        email_funcionario: Email del funcionario responsable
        
    Returns:
        ID del dispositivo creado, o False si hay error
    """
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
