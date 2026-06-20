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


def solicitar_transferencia(email_origen, email_destino, ids_entrada):
    if not ids_entrada:
        return False, "No se especificaron entradas para transferir"

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        conn.start_transaction()

        cursor.execute("SELECT 1 FROM Usuario WHERE email = %s", (email_destino,))
        if not cursor.fetchone():
            conn.rollback()
            return False, f"El usuario '{email_destino}' no existe en el sistema"

        placeholders = ", ".join(["%s"] * len(ids_entrada))
        cursor.execute(
            f"""
            SELECT idEntrada, emailPropietario, estado, cantTransferencias
            FROM Entrada
            WHERE idEntrada IN ({placeholders})
            FOR UPDATE
            """,
            ids_entrada,
        )
        entradas = cursor.fetchall()

        if len(entradas) != len(ids_entrada):
            conn.rollback()
            return False, "Alguna de las entradas seleccionadas no existe"

        ids_creados = []
        for entrada in entradas:
            if entrada["emailPropietario"] != email_origen:
                conn.rollback()
                return False, f"La entrada {entrada['idEntrada']} no pertenece al usuario origen"
            if entrada["estado"] != "activa":
                conn.rollback()
                return False, f"La entrada {entrada['idEntrada']} no está disponible (estado: {entrada['estado']})"
            if entrada["cantTransferencias"] >= 3:
                conn.rollback()
                return False, f"La entrada {entrada['idEntrada']} ya alcanzó el límite de transferencias"

            cursor.execute(
                "INSERT INTO Transferencia (idEntrada, emailOrigen, emailDestino, estado) VALUES (%s, %s, %s, 'pendiente')",
                (entrada["idEntrada"], email_origen, email_destino),
            )
            ids_creados.append(cursor.lastrowid)
            cursor.execute(
                "UPDATE Entrada SET estado = 'transferencia_pendiente' WHERE idEntrada = %s",
                (entrada["idEntrada"],),
            )

        conn.commit()
        return ids_creados, None
    except Exception as e:
        conn.rollback()
        return False, f"Error al solicitar transferencia: {e}"
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
