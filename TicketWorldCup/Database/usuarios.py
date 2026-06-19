"""
Funciones para la autenticación, registro y gestión de usuarios.
"""

import uuid
from hashlib import sha256

try:
    from .connection import get_db_connection
    from .utils import obtener_password_hash, interpretar_error_db
except ImportError:
    from connection import get_db_connection
    from utils import obtener_password_hash, interpretar_error_db


def autenticar_usuario(email, password):
    """
    Autentica un usuario verificando email y contraseña.
    
    Args:
        email: Email del usuario
        password: Contraseña en texto plano
        
    Returns:
        Diccionario con datos del usuario si es válido, None si no
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT
                u.email,
                u.passw,
                ug.estadoVerifIdentidad,
                ug.fechaRegistro,
                CASE WHEN ug.email IS NOT NULL THEN 1 ELSE 0 END AS esUsuarioGeneral,
                CASE WHEN a.email IS NOT NULL THEN 1 ELSE 0 END AS esAdministrador,
                CASE WHEN f.email IS NOT NULL THEN 1 ELSE 0 END AS esFuncionario
            FROM Usuario u
            LEFT JOIN Usuario_General ug ON ug.email = u.email
            LEFT JOIN Administrador_Pais_Sede a ON a.email = u.email
            LEFT JOIN Funcionario_Validacion f ON f.email = u.email
            WHERE u.email = %s
              AND u.passw = %s
            LIMIT 1
            """,
            (email, sha256(password.encode("utf-8")).hexdigest()),
        )
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


def registrar_usuario_general(datos, telefonos):
    """
    Registra un nuevo usuario general (comprador de entradas).
    
    Args:
        datos: Diccionario con información del usuario (email, doc, dirección, contraseña)
        telefonos: Lista de números de teléfono
        
    Returns:
        True si se registró exitosamente, False si hubo error
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        conn.start_transaction()

        cursor.execute(
            """
            INSERT INTO Usuario (
                email, docPais, docTipo, docNumero,
                dirPais, dirLocalidad, dirCalle, dirNumero, dirCodigoPostal, passw
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                datos["email"],
                datos["docPais"],
                datos["docTipo"],
                datos["docNumero"],
                datos["dirPais"],
                datos["dirLocalidad"],
                datos["dirCalle"],
                datos["dirNumero"],
                datos["dirCodigoPostal"],
                obtener_password_hash(datos),
            ),
        )

        cursor.execute(
            "INSERT INTO Usuario_General (email, estadoVerifIdentidad) VALUES (%s, 'pendiente')",
            (datos["email"],),
        )

        for telefono in telefonos:
            cursor.execute(
                "INSERT INTO Usuario_Telefono (email, telefono) VALUES (%s, %s)",
                (datos["email"], telefono),
            )

        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"Error en registro: {e}")
        return False
    finally:
        cursor.close()
        conn.close()


def registrar_usuario_admin(datos, pais_jurisdiccion, fecha_asignacion_cargo):
    """
    Registra un nuevo usuario administrador de país/sede.
    
    Args:
        datos: Diccionario con información del usuario
        pais_jurisdiccion: País bajo jurisdicción del administrador
        fecha_asignacion_cargo: Fecha de asignación del cargo
        
    Returns:
        True si se registró exitosamente, False si hubo error
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        conn.start_transaction()

        cursor.execute(
            """
            INSERT INTO Usuario (
                email, docPais, docTipo, docNumero,
                dirPais, dirLocalidad, dirCalle, dirNumero, dirCodigoPostal, passw
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                datos["email"],
                datos["docPais"],
                datos["docTipo"],
                datos["docNumero"],
                datos["dirPais"],
                datos["dirLocalidad"],
                datos["dirCalle"],
                datos["dirNumero"],
                datos["dirCodigoPostal"],
                obtener_password_hash(datos),
            ),
        )

        cursor.execute(
            """
            INSERT INTO Administrador_Pais_Sede (email, paisJurisdiccion, fechaAsignacionCargo)
            VALUES (%s, %s, %s)
            """,
            (datos["email"], pais_jurisdiccion, fecha_asignacion_cargo),
        )

        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"Error registrando administrador: {e}")
        return False
    finally:
        cursor.close()
        conn.close()


def registrar_funcionario_validacion(datos, numero_legajo):
    """
    Registra un nuevo funcionario de validación.
    
    Args:
        datos: Diccionario con información del usuario
        numero_legajo: Número de legajo del funcionario
        
    Returns:
        True si se registró exitosamente, False si hubo error
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        conn.start_transaction()

        cursor.execute(
            """
            INSERT INTO Usuario (
                email, docPais, docTipo, docNumero,
                dirPais, dirLocalidad, dirCalle, dirNumero, dirCodigoPostal, passw
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                datos["email"],
                datos["docPais"],
                datos["docTipo"],
                datos["docNumero"],
                datos["dirPais"],
                datos["dirLocalidad"],
                datos["dirCalle"],
                datos["dirNumero"],
                datos["dirCodigoPostal"],
                obtener_password_hash(datos),
            ),
        )

        cursor.execute(
            "INSERT INTO Funcionario_Validacion (email, numeroLegajo) VALUES (%s, %s)",
            (datos["email"], numero_legajo),
        )

        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"Error registrando funcionario: {e}")
        return False
    finally:
        cursor.close()
        conn.close()


def listar_compradores():
    """
    Lista todos los usuarios generales (compradores) registrados.
    
    Returns:
        Lista de diccionarios con información de compradores
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT
                u.email,
                ug.estadoVerifIdentidad,
                ug.fechaRegistro
            FROM Usuario_General ug
            JOIN Usuario u ON u.email = ug.email
            ORDER BY u.email
            """
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def listar_pendientes_validacion():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT u.email, u.docPais, u.docTipo, u.docNumero,
                   ug.estadoVerifIdentidad, ug.fechaRegistro
            FROM Usuario_General ug
            JOIN Usuario u ON u.email = ug.email
            WHERE ug.estadoVerifIdentidad = 'pendiente'
            ORDER BY ug.fechaRegistro ASC
            """
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def asegurar_funcionario(email):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT 1 FROM Funcionario_Validacion WHERE email = %s", (email,))
        if cursor.fetchone() is not None:
            return True
        cursor.execute("SELECT 1 FROM Administrador_Pais_Sede WHERE email = %s", (email,))
        if cursor.fetchone() is None:
            return False
        cursor.execute(
            "INSERT INTO Funcionario_Validacion (email, numeroLegajo) VALUES (%s, %s)",
            (email, f"ADMIN-{uuid.uuid4().hex[:8].upper()}"),
        )
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"Error asegurando funcionario: {e}")
        return False
    finally:
        cursor.close()
        conn.close()


def listar_funcionarios():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT fv.email, u.docPais, u.docTipo, u.docNumero, fv.numeroLegajo
            FROM Funcionario_Validacion fv
            JOIN Usuario u ON u.email = fv.email
            ORDER BY fv.email
            """
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def listar_asignaciones_funcionario(email):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT af.idEvento, e.nombreEvento, e.fecha, TIME_FORMAT(e.hora, '%H:%i') AS hora,
                   af.idSector, s.codigo AS sectorCodigo,
                   st.nombre AS estadio,
                   af.emailFuncionario
            FROM Asignacion_Funcionario af
            JOIN Evento e ON e.idEvento = af.idEvento
            JOIN Sector s ON s.idSector = af.idSector
            JOIN Estadio st ON st.idEstadio = s.idEstadio
            WHERE af.emailFuncionario = %s
            ORDER BY e.fecha, s.codigo
            """,
            (email,),
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def listar_asignaciones_evento(id_evento):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT af.idEvento, af.idSector, s.codigo AS sectorCodigo,
                   af.emailFuncionario, u.docPais, u.docTipo, u.docNumero
            FROM Asignacion_Funcionario af
            JOIN Sector s ON s.idSector = af.idSector
            JOIN Usuario u ON u.email = af.emailFuncionario
            WHERE af.idEvento = %s
            ORDER BY s.codigo, af.emailFuncionario
            """,
            (id_evento,),
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def asignar_funcionario_sector(id_evento, id_sector, email_funcionario):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO Asignacion_Funcionario (idEvento, idSector, emailFuncionario) VALUES (%s, %s, %s)",
            (id_evento, id_sector, email_funcionario),
        )
        conn.commit()
        return True, None
    except Exception as e:
        conn.rollback()
        err = interpretar_error_db(e, "asignación")
        return False, err
    finally:
        cursor.close()
        conn.close()


def eliminar_asignacion_funcionario(id_evento, id_sector, email_funcionario):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "DELETE FROM Asignacion_Funcionario WHERE idEvento = %s AND idSector = %s AND emailFuncionario = %s",
            (id_evento, id_sector, email_funcionario),
        )
        conn.commit()
        return cursor.rowcount > 0, None
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        cursor.close()
        conn.close()


def obtener_usuario_por_email(email):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT u.email, u.docPais, u.docTipo, u.docNumero,
                   u.dirPais, u.dirLocalidad, u.dirCalle, u.dirNumero, u.dirCodigoPostal,
                   ug.email AS esGeneral,
                   ap.email AS esAdmin,
                   fv.email AS esFuncionario
            FROM Usuario u
            LEFT JOIN Usuario_General ug ON ug.email = u.email
            LEFT JOIN Administrador_Pais_Sede ap ON ap.email = u.email
            LEFT JOIN Funcionario_Validacion fv ON fv.email = u.email
            WHERE u.email = %s
            """,
            (email,),
        )
        row = cursor.fetchone()
        if not row:
            return None
        row["esGeneral"] = row["esGeneral"] is not None
        row["esAdmin"] = row["esAdmin"] is not None
        row["esFuncionario"] = row["esFuncionario"] is not None
        return row
    finally:
        cursor.close()
        conn.close()


def obtener_telefonos_usuario(email):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT telefono FROM Usuario_Telefono WHERE email = %s",
            (email,),
        )
        return [row["telefono"] for row in cursor.fetchall()]
    finally:
        cursor.close()
        conn.close()


def actualizar_usuario(email, datos):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        campos = []
        valores = []
        for col in ("docPais", "docTipo", "docNumero",
                     "dirPais", "dirLocalidad", "dirCalle", "dirNumero", "dirCodigoPostal"):
            if col in datos and datos[col] is not None:
                campos.append(f"{col} = %s")
                valores.append(datos[col])
        if not campos:
            return True, None

        sentencia = f"UPDATE Usuario SET {', '.join(campos)} WHERE email = %s"
        valores.append(email)
        cursor.execute(sentencia, tuple(valores))
        conn.commit()
        return True, None
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        cursor.close()
        conn.close()


def actualizar_telefonos_usuario(email, telefonos):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM Usuario_Telefono WHERE email = %s", (email,))
        for t in telefonos:
            t = t.strip()
            if t:
                cursor.execute(
                    "INSERT INTO Usuario_Telefono (email, telefono) VALUES (%s, %s)",
                    (email, t),
                )
        conn.commit()
        return True, None
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        cursor.close()
        conn.close()


def actualizar_roles_usuario(email, roles):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        accion = roles.get("accion")
        rol = roles.get("rol")
        if accion not in ("agregar", "quitar") or rol not in ("admin", "funcionario"):
            return False, "Acción o rol inválido"

        if rol == "admin":
            tabla = "Administrador_Pais_Sede"
        else:
            tabla = "Funcionario_Validacion"

        if accion == "agregar":
            cursor.execute("SELECT 1 FROM {} WHERE email = %s".format(tabla), (email,))
            if cursor.fetchone():
                return False, "El usuario ya tiene ese rol asignado"

            if rol == "admin":
                cursor.execute(
                    "INSERT INTO Administrador_Pais_Sede (email, paisJurisdiccion, fechaAsignacionCargo) "
                    "VALUES (%s, %s, %s)",
                    (email, roles.get("paisJurisdiccion"), roles.get("fechaAsignacionCargo")),
                )
            else:
                numero_legajo = roles.get("numeroLegajo") or f"AUTO-{uuid.uuid4().hex[:8].upper()}"
                cursor.execute(
                    "INSERT INTO Funcionario_Validacion (email, numeroLegajo) VALUES (%s, %s)",
                    (email, numero_legajo),
                )
        else:
            cursor.execute("DELETE FROM {} WHERE email = %s".format(tabla), (email,))
            if cursor.rowcount == 0:
                return False, "El usuario no tiene ese rol asignado"

        conn.commit()
        return True, None
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        cursor.close()
        conn.close()


def actualizar_estado_verificacion(email, nuevo_estado):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE Usuario_General SET estadoVerifIdentidad = %s WHERE email = %s",
            (nuevo_estado, email),
        )
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        conn.rollback()
        print(f"Error actualizando verificación: {e}")
        return False
    finally:
        cursor.close()
        conn.close()
