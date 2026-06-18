"""
Funciones para la gestión de transferencias de entradas entre usuarios.
"""

try:
    from .connection import get_db_connection
except ImportError:
    from connection import get_db_connection


def listar_transferencias_usuario(email_usuario):
    """
    Lista todas las transferencias de un usuario (como origen o destino).
    
    Args:
        email_usuario: Email del usuario
        
    Returns:
        Lista de diccionarios con información de transferencias
    """
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
    """
    Solicita la transferencia de una entrada a otro usuario.
    
    La entrada puede ser transferida máximo 3 veces.
    
    Args:
        id_entrada: ID de la entrada a transferir
        email_origen: Email del propietario actual
        email_destino: Email del nuevo propietario
        
    Returns:
        ID de la transferencia creada, o False si hay error
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        conn.start_transaction()

        # Validar que la entrada existe y el usuario es propietario
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

        # Validar que la entrada no esté consumida y no exceda límite de transferencias
        if entrada["estado"] == "consumida" or entrada["cantTransferencias"] >= 3:
            conn.rollback()
            return False

        # Crear la transferencia
        cursor.execute(
            """
            INSERT INTO Transferencia (idEntrada, emailOrigen, emailDestino, estado)
            VALUES (%s, %s, %s, 'pendiente')
            """,
            (id_entrada, email_origen, email_destino),
        )
        
        # Marcar entrada como transferencia pendiente
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
    """
    Responde a una solicitud de transferencia (acepta o rechaza).
    
    Args:
        id_transferencia: ID de la transferencia
        estado: 'aceptada' o 'rechazada'
        
    Returns:
        True si se procesó exitosamente, False si hay error
    """
    if estado not in ("aceptada", "rechazada"):
        return False

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        conn.start_transaction()

        # Obtener datos de la transferencia
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
            # Validar que la entrada puede ser aceptada
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

            # Actualizar propietario de la entrada
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
            # Rechazada: volver la entrada a estado activo
            cursor.execute(
                """
                UPDATE Entrada
                SET estado = 'activa'
                WHERE idEntrada = %s AND estado = 'transferencia_pendiente'
                """,
                (transferencia["idEntrada"],),
            )

        # Actualizar estado de la transferencia
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
