"""
Funciones para la autenticación, registro y gestión de usuarios.
"""

from hashlib import sha256

try:
    from .connection import get_db_connection
    from .utils import obtener_password_hash
except ImportError:
    from connection import get_db_connection
    from utils import obtener_password_hash


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
