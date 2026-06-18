"""
Funciones para la validación de entradas mediante tokens QR.
"""

import uuid

try:
    from .connection import get_db_connection
except ImportError:
    from connection import get_db_connection


def registrar_token_qr(id_entrada, valor=None, tiempo_vencimiento=30):
    """
    Genera y registra un token QR para una entrada.
    
    Args:
        id_entrada: ID de la entrada
        valor: Valor único del token (se genera automáticamente si no se proporciona)
        tiempo_vencimiento: Tiempo de validez en minutos
        
    Returns:
        ID del token creado, o False si hay error
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        conn.start_transaction()

        # Expira tokens anteriores
        cursor.execute(
            "UPDATE Token_QR SET estado = 'expirado' WHERE idEntrada = %s AND estado = 'activo'",
            (id_entrada,),
        )

        # Generar valor si no se proporciona
        if valor is None:
            valor = f"QR-{uuid.uuid4().hex.upper()}"

        # Insertar nuevo token
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
    """
    Obtiene el token QR activo y válido de una entrada.
    
    Args:
        id_entrada: ID de la entrada
        
    Returns:
        Diccionario con datos del token, o None si no hay token válido
    """
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
    """
    Valida una entrada usando su token QR.
    
    Marca la entrada como consumida y registra la validación en el sistema.
    
    Args:
        id_token: ID del token QR
        id_dispositivo: ID del dispositivo de validación
        email_funcionario: Email del funcionario que valida
        
    Returns:
        True si se validó exitosamente, False si hay error
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        conn.start_transaction()

        # Obtener y validar token
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

        # Validar que el token esté activo
        if token["estadoToken"] != "activo":
            conn.rollback()
            return False

        # Validar que el dispositivo y funcionario están registrados
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

        # Registrar la validación
        cursor.execute(
            """
            INSERT INTO Validacion_Entrada (
                idEntrada, idToken, idDispositivo, emailFuncionario, fechaHoraValidacion
            ) VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)
            """,
            (token["idEntrada"], id_token, id_dispositivo, email_funcionario),
        )

        # Marcar entrada como consumida
        cursor.execute(
            "UPDATE Entrada SET estado = 'consumida' WHERE idEntrada = %s",
            (token["idEntrada"],),
        )
        
        # Marcar token como usado
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
