"""
Funciones para reportes y análisis del sistema.
"""


def listar_funcionarios_evento(id_evento):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT DISTINCT af.emailFuncionario
            FROM Asignacion_Funcionario af
            WHERE af.idEvento = %s
            ORDER BY af.emailFuncionario
            """,
            (id_evento,),
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

try:
    from .connection import get_db_connection
except ImportError:
    from connection import get_db_connection


def ranking_eventos_mas_vendidos(limite=10):
    """
    Ranking de eventos con más entradas vendidas.
    
    Args:
        limite: Número máximo de resultados a retornar
        
    Returns:
        Lista de diccionarios con información de eventos ordenados por ventas
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT
                ev.idEvento,
                ev.nombreEvento,
                ev.fecha,
                TIME_FORMAT(ev.hora, '%H:%i') AS hora,
                COUNT(en.idEntrada) AS entradasVendidas,
                COALESCE(SUM(v.montoTotal), 0) AS facturacion
            FROM Evento ev
            LEFT JOIN Entrada en ON en.idEvento = ev.idEvento
            LEFT JOIN Venta v ON v.idVenta = en.idVenta
            GROUP BY ev.idEvento, ev.nombreEvento, ev.fecha, ev.hora
            ORDER BY entradasVendidas DESC, ev.fecha ASC, ev.hora ASC
            LIMIT %s
            """,
            (limite,),
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def ranking_mayores_compradores(limite=10):
    """
    Ranking de usuarios que más han gastado en entradas.
    
    Args:
        limite: Número máximo de resultados a retornar
        
    Returns:
        Lista de diccionarios con información de compradores ordenados por gasto
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT
                v.emailComprador,
                COUNT(en.idEntrada) AS totalEntradas,
                COUNT(DISTINCT v.idVenta) AS totalCompras,
                COALESCE(SUM(v.montoTotal), 0) AS totalGastado
            FROM Venta v
            LEFT JOIN Entrada en ON en.idVenta = v.idVenta
            GROUP BY v.emailComprador
            ORDER BY totalEntradas DESC, totalGastado DESC
            LIMIT %s
            """,
            (limite,),
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def cobertura_evento_completa(id_evento):
    """
    Cobertura de TODOS los funcionarios asignados a un evento.
    Devuelve una lista agrupada por funcionario con sus sectores y si cumplió.
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT
                af.emailFuncionario,
                af.idSector,
                s.codigo AS sectorCodigo,
                COUNT(DISTINCT ve.idValidacion) AS validaciones
            FROM Asignacion_Funcionario af
            JOIN Sector s ON s.idSector = af.idSector
            LEFT JOIN Entrada en ON en.idEvento = af.idEvento AND en.idSector = af.idSector
            LEFT JOIN Validacion_Entrada ve
                ON ve.idEntrada = en.idEntrada AND ve.emailFuncionario = af.emailFuncionario
            WHERE af.idEvento = %s
            GROUP BY af.emailFuncionario, af.idSector, s.codigo
            ORDER BY af.emailFuncionario, s.codigo
            """,
            (id_evento,),
        )
        filas = cursor.fetchall()

        # Agrupar por funcionario
        funcionarios = {}
        for fila in filas:
            email = fila["emailFuncionario"]
            if email not in funcionarios:
                funcionarios[email] = {"emailFuncionario": email, "sectores": [], "cobertura_completa": True}
            cumple = fila["validaciones"] > 0
            funcionarios[email]["sectores"].append({
                "idSector": fila["idSector"],
                "sectorCodigo": fila["sectorCodigo"],
                "validaciones": fila["validaciones"],
                "cumple": cumple,
            })
            if not cumple:
                funcionarios[email]["cobertura_completa"] = False

        return list(funcionarios.values())
    finally:
        cursor.close()
        conn.close()


def cobertura_funcionario_evento(id_evento, email_funcionario):
    """
    Reporte de cobertura de un funcionario en un evento.
    
    Muestra qué sectores le fueron asignados y cuántos accesos validó en cada uno.
    
    Args:
        id_evento: ID del evento
        email_funcionario: Email del funcionario
        
    Returns:
        Lista de diccionarios con información de cobertura por sector
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT
                af.idSector,
                s.codigo,
                COUNT(DISTINCT ve.idValidacion) AS validaciones
            FROM Asignacion_Funcionario af
            JOIN Sector s ON s.idSector = af.idSector
            LEFT JOIN Entrada en ON en.idEvento = af.idEvento AND en.idSector = af.idSector
            LEFT JOIN Validacion_Entrada ve ON ve.idEntrada = en.idEntrada AND ve.emailFuncionario = af.emailFuncionario
            WHERE af.idEvento = %s AND af.emailFuncionario = %s
            GROUP BY af.idSector, s.codigo
            ORDER BY s.codigo
            """,
            (id_evento, email_funcionario),
        )
        resultado = cursor.fetchall()
        
        # Agregar bandera de cumplimiento
        for fila in resultado:
            fila["cumple"] = fila["validaciones"] > 0
        
        return resultado
    finally:
        cursor.close()
        conn.close()
