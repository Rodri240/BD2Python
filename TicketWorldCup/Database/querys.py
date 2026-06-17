def registrar_usuario_general(datos, telefonos):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        conn.start_transaction()
        
        # 1. Insertar en Usuario
        sql_user = """INSERT INTO Usuario (email, docPais, docTipo, docNumero, dirPais, dirLocalidad, dirCalle, dirNumero, dirCodigoPostal) 
                      VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        cursor.execute(sql_user, (datos['email'], datos['docPais'], datos['docTipo'], datos['docNumero'], datos['dirPais'], datos['dirLocalidad'], datos['dirCalle'], datos['dirNumero'], datos['dirCodigoPostal']))
        
        # 2. Insertar en Usuario_General
        sql_gen = "INSERT INTO Usuario_General (email, estadoVerifIdentidad) VALUES (%s, 'pendiente')"
        cursor.execute(sql_gen, (datos['email'],))
        
        # 3. Insertar Teléfonos (si existen)
        for tel in telefonos:
            cursor.execute("INSERT INTO Usuario_Telefono (email, telefono) VALUES (%s, %s)", (datos['email'], tel))
            
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"Error en registro: {e}")
        return False
    finally:
        cursor.close()
        conn.close()


def ejecutar_transaccion_venta(email, id_evento, id_sector, cantidad):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        conn.start_transaction()
        
        # 1. Verificar Capacidad Máxima del Sector bloqueando la fila para concurrencia (FOR UPDATE)
        cursor.execute("""
            SELECT s.capacidadMaxima, s.costoEntrada 
            FROM Sector s
            JOIN Evento e ON e.idEstadio = s.idEstadio
            WHERE e.idEvento = %s AND s.codigo = %s FOR UPDATE
        """, (id_evento, id_sector))
        sector_info = cursor.fetchone()
        
        # Contar cuántas entradas ya se vendieron para este evento y sector
        cursor.execute("SELECT COUNT(*) AS total FROM Entrada WHERE idEvento = %s AND idSector = %s", (id_evento, id_sector))
        vendidas = cursor.fetchone()['total']
        
        if vendidas + cantidad > sector_info['capacidadMaxima']:
            conn.rollback() # Sobre-aforo detectado
            return False
            
        # 2. Calcular montos (Costo + 5% comisión)
        subtotal = sector_info['costoEntrada'] * cantidad
        monto_total = subtotal * 1.05
        
        # 3. Crear el registro en Venta
        num_venta = f"VTA-{id_evento}-{email[:3].upper()}"
        cursor.execute("""
            INSERT INTO Venta (numero, estado, montoTotal, emailComprador) 
            VALUES (%s, 'paga', %s, %s)
        """, (num_venta, monto_total, email))
        id_venta = cursor.lastrowid
        
        # 4. Crear las entradas individuales
        for _ in range(cantidad):
            cursor.execute("""
                INSERT INTO Entrada (idVenta, idEvento, idSector, emailPropietario, estado, cantTransferencias)
                VALUES (%s, %s, %s, %s, 'activa', 0)
            """, (id_venta, id_evento, id_sector, email))
            
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()