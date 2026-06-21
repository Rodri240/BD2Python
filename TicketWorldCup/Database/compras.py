"""
Funciones para la gestión de compras, ventas y entradas.
"""

import uuid

try:
    from .connection import get_db_connection
    from .utils import normalizar_items_venta, obtener_tasa_comision_actual
except ImportError:
    from connection import get_db_connection
    from utils import normalizar_items_venta, obtener_tasa_comision_actual


def registrar_venta_y_entradas(email_comprador, items, estado='pendiente'):
    """
    Registra una venta completa con todas sus entradas.
    
    Args:
        email_comprador: Email del comprador
        items: Lista de items con {id_evento, id_sector, cantidad}
        estado: Estado inicial de la venta ('paga', 'pendiente', etc.)
        
    Returns:
        ID de la venta creada, o False si hay error
    """
    items_normalizados = normalizar_items_venta(items)
    total_entradas = sum(item["cantidad"] for item in items_normalizados)

    if total_entradas <= 0 or total_entradas > 5:
        return False

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        conn.start_transaction()

        detalle_compra = []
        monto_base = 0

        # Validar disponibilidad en todos los sectores
        for item in items_normalizados:
            cursor.execute(
                """
                SELECT
                    s.costoEntrada,
                    s.capacidadMaxima
                FROM Evento_Sector es
                JOIN Evento e ON e.idEvento = es.idEvento
                JOIN Sector s ON s.idEstadio = e.idEstadio AND s.idSector = es.idSector
                WHERE es.idEvento = %s AND es.idSector = %s
                FOR UPDATE
                """,
                (item["id_evento"], item["id_sector"]),
            )
            sector = cursor.fetchone()
            if not sector:
                conn.rollback()
                return False

            cursor.execute(
                "SELECT COUNT(*) AS total FROM Entrada WHERE idEvento = %s AND idSector = %s",
                (item["id_evento"], item["id_sector"]),
            )
            vendidas = cursor.fetchone()["total"]

            if vendidas + item["cantidad"] > sector["capacidadMaxima"]:
                conn.rollback()
                return False

            monto_base += float(sector["costoEntrada"]) * item["cantidad"]
            detalle_compra.append(item)

        # Calcular monto total con comisión
        tasa_comision = obtener_tasa_comision_actual(cursor)
        monto_total = round(monto_base * (1 + tasa_comision), 2)
        numero_venta = f"VTA-{uuid.uuid4().hex[:12].upper()}"

        # Insertar venta
        cursor.execute(
            """
            INSERT INTO Venta (numero, estado, montoTotal, emailComprador)
            VALUES (%s, %s, %s, %s)
            """,
            (numero_venta, estado, monto_total, email_comprador),
        )
        id_venta = cursor.lastrowid

        # Crear las entradas individuales
        for item in detalle_compra:
            for _ in range(item["cantidad"]):
                cursor.execute(
                    """
                    INSERT INTO Entrada (
                        idVenta, idEvento, idSector, emailPropietario, estado, cantTransferencias
                    ) VALUES (%s, %s, %s, %s, 'activa', 0)
                    """,
                    (id_venta, item["id_evento"], item["id_sector"], email_comprador),
                )

        conn.commit()
        return id_venta
    except Exception as e:
        conn.rollback()
        print(f"Error en venta: {e}")
        return False
    finally:
        cursor.close()
        conn.close()


def ejecutar_transaccion_venta(email, id_evento, id_sector, cantidad):
    """
    Ejecuta una transacción de venta simple (una entrada).
    
    Args:
        email: Email del comprador
        id_evento: ID del evento
        id_sector: ID del sector
        cantidad: Cantidad de entradas a comprar
        
    Returns:
        True si se vendió exitosamente, False si hay error
    """
    return bool(
        registrar_venta_y_entradas(
            email,
            [{"id_evento": id_evento, "id_sector": id_sector, "cantidad": cantidad}],
        )
    )


def _transicionar_venta(id_venta, estado_requerido, estado_nuevo):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        conn.start_transaction()
        cursor.execute(
            "SELECT idVenta, estado FROM Venta WHERE idVenta = %s FOR UPDATE",
            (id_venta,),
        )
        venta = cursor.fetchone()
        if not venta:
            conn.rollback()
            return False, "Venta no encontrada"
        if venta["estado"] != estado_requerido:
            conn.rollback()
            return False, f"La venta debe estar en estado '{estado_requerido}' (estado actual: {venta['estado']})"
        cursor.execute(
            "UPDATE Venta SET estado = %s WHERE idVenta = %s",
            (estado_nuevo, id_venta),
        )
        conn.commit()
        return True, None
    except Exception as e:
        conn.rollback()
        print(f"Error actualizando venta: {e}")
        return False, "Error interno"
    finally:
        cursor.close()
        conn.close()


def confirmar_pedido_venta(id_venta):
    return _transicionar_venta(id_venta, "pendiente", "confirmada")


def pagar_venta_usuario(id_venta, email_comprador):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT emailComprador FROM Venta WHERE idVenta = %s", (id_venta,))
        venta = cursor.fetchone()
        if not venta:
            return False, "Venta no encontrada"
        if venta["emailComprador"] != email_comprador:
            return False, "No podés pagar una venta que no es tuya"
    finally:
        cursor.close()
        conn.close()
    return _transicionar_venta(id_venta, "pendiente", "confirmada")


def confirmar_pago_venta(id_venta):
    return _transicionar_venta(id_venta, "confirmada", "paga")


def listar_ventas_pendientes():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT
                v.idVenta,
                v.numero,
                v.fechaVenta,
                v.estado,
                v.montoTotal,
                v.emailComprador,
                COUNT(e.idEntrada) AS cantidadEntradas
            FROM Venta v
            LEFT JOIN Entrada e ON e.idVenta = v.idVenta
            WHERE v.estado IN ('pendiente', 'confirmada')
            GROUP BY v.idVenta, v.numero, v.fechaVenta, v.estado, v.montoTotal, v.emailComprador
            ORDER BY v.fechaVenta DESC
            """
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def listar_compras_usuario(email_comprador):
    """
    Lista todas las compras realizadas por un usuario.
    
    Args:
        email_comprador: Email del comprador
        
    Returns:
        Lista de diccionarios con información de compras
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT
                v.idVenta,
                v.numero,
                v.fechaVenta,
                v.estado,
                v.montoTotal,
                COUNT(e.idEntrada) AS cantidadEntradas
            FROM Venta v
            LEFT JOIN Entrada e ON e.idVenta = v.idVenta
            WHERE v.emailComprador = %s
            GROUP BY v.idVenta, v.numero, v.fechaVenta, v.estado, v.montoTotal
            ORDER BY v.fechaVenta DESC
            """,
            (email_comprador,),
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def listar_entradas_usuario(email_propietario):
    """
    Lista todas las entradas que posee un usuario.
    
    Args:
        email_propietario: Email del propietario de las entradas
        
    Returns:
        Lista de diccionarios con información de entradas
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT
                en.idEntrada,
                en.estado,
                en.cantTransferencias,
                en.emailPropietario,
                en.idSector,
                sec.codigo AS sectorCodigo,
                ev.idEvento,
                ev.nombreEvento,
                ev.fecha,
                TIME_FORMAT(ev.hora, '%H:%i') AS hora,
                s.nombre AS estadio,
                s.ciudad,
                v.numero AS numeroVenta,
                v.fechaVenta
            FROM Entrada en
            JOIN Venta v ON v.idVenta = en.idVenta
            JOIN Evento ev ON ev.idEvento = en.idEvento
            JOIN Estadio s ON s.idEstadio = ev.idEstadio
            JOIN Sector sec ON sec.idSector = en.idSector
            WHERE en.emailPropietario = %s
            ORDER BY ev.fecha, ev.hora, en.idEntrada
            """,
            (email_propietario,),
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()
