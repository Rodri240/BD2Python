"""
Funciones para la gestión de dispositivos de validación.
"""

try:
    from .connection import get_db_connection
except ImportError:
    from connection import get_db_connection


def listar_dispositivos_por_funcionario(email_funcionario):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT idDispositivo, dirMAC, alias, emailFuncionario FROM Dispositivo WHERE emailFuncionario = %s ORDER BY idDispositivo",
            (email_funcionario,),
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def registrar_dispositivo(dir_mac, email_funcionario, alias=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO Dispositivo (dirMAC, alias, emailFuncionario) VALUES (%s, %s, %s)",
            (dir_mac, alias, email_funcionario),
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
