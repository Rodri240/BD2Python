@app.route('/comprar', methods=['POST'])
def procesar_compra():
    email_comprador = session.get('user_email')
    id_evento = request.form.get('idEvento')
    id_sector = request.form.get('idSector')  # Código 'A', 'B', 'C' o 'D'
    cantidad = int(request.form.get('cantidad')) # Cuántas entradas quiere
    
    # Regla de negocio básica
    if cantidad > 5:
        return "No puedes comprar más de 5 entradas en la misma transacción.", 400
        
    # Ejecutar la transacción en la base de datos
    exito = ejecutar_transaccion_venta(email_comprador, id_evento, id_sector, cantidad)
    if exito:
        return "Compra realizada con éxito"
    else:
        return "Error en la compra: Sector agotado o error de sistema.", 500