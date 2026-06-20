from datetime import date, datetime, time, timedelta
from decimal import Decimal

from flask import Flask, jsonify, redirect, render_template, request, session, url_for

from Database import (
    autenticar_usuario,
    registrar_usuario_general,
    registrar_usuario_admin,
    registrar_funcionario_validacion,
    registrar_dispositivo,
    listar_dispositivos_por_funcionario,
    crear_estadio,
    crear_sector,
    crear_evento,
    vincular_equipo_evento,
    habilitar_sector_evento,
    listar_estadios,
    listar_sectores,
    listar_eventos,
    listar_vinculaciones,
    listar_equipos,
    listar_sectores_evento,
    listar_codigos_sector_disponibles,
    listar_equipos_disponibles_evento,
    listar_sectores_disponibles_evento,
    listar_entradas_no_validadas_por_evento,
    listar_entradas_validadas_por_evento,
    listar_compradores,
    listar_pendientes_validacion,
    actualizar_estado_verificacion,
    asegurar_funcionario,
    listar_funcionarios,
    listar_asignaciones_evento,
    asignar_funcionario_sector,
    eliminar_asignacion_funcionario,
    listar_asignaciones_funcionario,
    obtener_usuario_por_email,
    obtener_telefonos_usuario,
    actualizar_usuario,
    actualizar_telefonos_usuario,
    actualizar_roles_usuario,
    registrar_venta_y_entradas,
    ejecutar_transaccion_venta,
    confirmar_pedido_venta,
    confirmar_pago_venta,
    listar_ventas_pendientes,
    listar_compras_usuario,
    listar_entradas_usuario,
    listar_transferencias_usuario,
    solicitar_transferencia,
    responder_transferencia,
    registrar_token_qr,
    obtener_token_activo,
    validar_entrada,
    ranking_eventos_mas_vendidos,
    ranking_mayores_compradores,
    cobertura_funcionario_evento,
    cobertura_evento_completa,
    listar_funcionarios_evento,
)


app = Flask(__name__, template_folder="Template")
app.secret_key = "ticketworldcup-dev"
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(hours=8)
app.config["SESSION_REFRESH_EACH_REQUEST"] = True


PAGE_ENDPOINTS = {
    "index",
    "home",
    "registro",
    "perfil",
    "infraestructura",
    "compras",
    "transferencias",
    "validacion",
    "consultas",
    "login",
}

PUBLIC_ENDPOINTS = {
    "login",
    "index",
    "registrarse",
    "ruta_registro_publico",
    "principal",
    "clear_session_user",
    "static",
}


@app.before_request
def requerir_login():
    endpoint = request.endpoint
    if endpoint is None or endpoint in PUBLIC_ENDPOINTS:
        return None

    if session.get("user_email"):
        return None

    if endpoint in PAGE_ENDPOINTS:
        return redirect(url_for("login"))

    if request.path.startswith("/"):
        return _json_error("No autenticado", 401)

    return None


def _json_ok(data=None, status=200):
    payload = {"ok": True}
    if isinstance(data, dict):
        payload.update(_json_safe(data))
    elif data is not None:
        payload["data"] = _json_safe(data)
    return jsonify(payload), status


def _json_error(message, status=400):
    return jsonify({"ok": False, "error": message}), status


def _json_safe(value):
    if isinstance(value, dict):
        return {key: _json_safe(inner) for key, inner in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    if isinstance(value, tuple):
        return [_json_safe(item) for item in value]
    if isinstance(value, (datetime, date, time)):
        return value.isoformat()
    if isinstance(value, timedelta):
        return value.total_seconds()
    if isinstance(value, Decimal):
        return float(value)
    return value


def _input_payload():
    return request.get_json(silent=True) or request.form


def _es_admin_activo():
    return bool(session.get("user_roles", {}).get("admin"))


def _requiere_admin():
    if not session.get("user_email"):
        return _json_error("No autenticado", 401)
    if not _es_admin_activo():
        return _json_error("Esta accion requiere un usuario administrador", 403)
    return None


@app.route("/principal", methods=["GET"])
def principal():
    if session.get("user_email"):
        return redirect(url_for("home"))
    return render_template("principal.html")


@app.route("/", methods=["GET"])
def index():
    if not session.get("user_email"):
        return redirect(url_for("principal"))
    return render_template(
        "index.html",
        session_email=session.get("user_email"),
        session_roles=session.get("user_roles", {}),
    )


app.add_url_rule("/", endpoint="home", view_func=index)


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_email"):
        return redirect(url_for("home"))

    error = None
    if request.method == "POST":
        datos = _input_payload()
        email = (datos.get("email") or "").strip()
        password = datos.get("password") or ""

        if not email or not password:
            error = "Debes completar email y contraseña."
        else:
            usuario = autenticar_usuario(email, password)
            if usuario:
                session.clear()
                session.permanent = True
                session["user_email"] = usuario["email"]
                session["user_roles"] = {
                    "general": bool(usuario["esUsuarioGeneral"]),
                    "admin": bool(usuario["esAdministrador"]),
                    "funcionario": bool(usuario["esFuncionario"]),
                }
                return redirect(url_for("home"))
            error = "Credenciales inválidas."

    return render_template("login.html", error=error, session_email=None)


@app.route("/registro", methods=["GET"])
def registro():
    if not _es_admin_activo():
        return redirect(url_for("home"))
    return render_template("registro.html", session_email=session.get("user_email"))


@app.route("/registrarse", methods=["GET"])
def registrarse():
    if session.get("user_email"):
        return redirect(url_for("home"))
    return render_template("registro_publico.html")


@app.route("/registrarse", methods=["POST"])
def ruta_registro_publico():
    datos = _input_payload()
    telefonos = datos.get("telefonos", [])
    if isinstance(telefonos, str):
        telefonos = [t.strip() for t in telefonos.split(",") if t.strip()]
    exito = registrar_usuario_general(datos, telefonos)
    if exito:
        return _json_ok({"registrado": True})
    return _json_error("No se pudo completar el registro. Verificá que el email no esté en uso.", 400)


@app.route("/perfil", methods=["GET"])
def perfil():
    return render_template("perfil.html", session_email=session.get("user_email"))


@app.route("/infraestructura", methods=["GET"])
def infraestructura():
    return render_template(
        "infraestructura.html",
        session_email=session.get("user_email"),
        session_roles=session.get("user_roles", {}),
    )


@app.route("/compras", methods=["GET"])
def compras():
    return render_template(
        "compras.html",
        session_email=session.get("user_email"),
        session_roles=session.get("user_roles", {}),
    )


@app.route("/transferencias", methods=["GET"])
def transferencias():
    return render_template("transferencias.html", session_email=session.get("user_email"))


@app.route("/validacion", methods=["GET"])
def validacion():
    return render_template(
        "validacion.html",
        session_email=session.get("user_email"),
        session_roles=session.get("user_roles", {}),
    )


@app.route("/consultas", methods=["GET"])
def consultas():
    return render_template(
        "consultas.html",
        session_email=session.get("user_email"),
        session_roles=session.get("user_roles", {}),
    )


@app.route("/sesion", methods=["POST"])
def set_session_user():
    datos = _input_payload()
    email = datos.get("email")
    if not email:
        return _json_error("Falta el email")
    session.permanent = True
    session["user_email"] = email
    return _json_ok({"user_email": email})


@app.route("/salir", methods=["POST"])
def clear_session_user():
    session.pop("user_email", None)
    session.pop("user_roles", None)
    return _json_ok()


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/registrar/general", methods=["POST"])
def ruta_registrar_general():
    datos = _input_payload()
    telefonos = datos.get("telefonos", [])
    if isinstance(telefonos, str):
        telefonos = [telefono.strip() for telefono in telefonos.split(",") if telefono.strip()]
    exito = registrar_usuario_general(datos, telefonos)
    return _json_ok({"registrado": exito}) if exito else _json_error("No se pudo registrar el usuario general", 500)


@app.route("/registrar/admin", methods=["POST"])
def ruta_registrar_admin():
    datos = _input_payload()
    exito = registrar_usuario_admin(datos, datos.get("paisJurisdiccion"), datos.get("fechaAsignacionCargo"))
    return _json_ok({"registrado": exito}) if exito else _json_error("No se pudo registrar el administrador", 500)


@app.route("/registrar/funcionario", methods=["POST"])
def ruta_registrar_funcionario():
    datos = _input_payload()
    exito = registrar_funcionario_validacion(datos, datos.get("numeroLegajo"))
    return _json_ok({"registrado": exito}) if exito else _json_error("No se pudo registrar el funcionario", 500)


@app.route("/dispositivo", methods=["POST"])
def ruta_registrar_dispositivo():
    datos = _input_payload()
    dir_mac = datos.get("dirMAC")
    email_func = datos.get("emailFuncionario")
    alias = datos.get("alias")
    if not email_func:
        return _json_error("Falta el email del funcionario", 400)
    asegurar_funcionario(email_func)
    nuevo_id = registrar_dispositivo(dir_mac, email_func, alias)
    if nuevo_id:
        return _json_ok({"idDispositivo": nuevo_id, "alias": alias, "emailFuncionario": email_func})
    return _json_error("No se pudo registrar el dispositivo", 500)


@app.route("/estadio", methods=["POST"])
def ruta_crear_estadio():
    bloqueo = _requiere_admin()
    if bloqueo:
        return bloqueo
    datos = _input_payload()
    nombre = (datos.get("nombre") or "").strip()
    pais = (datos.get("pais") or "").strip()
    ciudad = (datos.get("ciudad") or "").strip()
    email_admin = (datos.get("emailAdmin") or session.get("user_email") or "").strip()
    fecha_asignacion = (datos.get("fechaAsignacion") or "").strip()
    if not nombre:
        return _json_error("Falta el nombre del estadio", 400)
    if not pais:
        return _json_error("Falta el país del estadio", 400)
    if not ciudad:
        return _json_error("Falta la ciudad del estadio", 400)
    if not email_admin:
        return _json_error("Falta el email del administrador", 400)
    if not fecha_asignacion:
        return _json_error("Falta la fecha de asignación", 400)
    nuevo_id, error = crear_estadio(nombre, pais, ciudad, email_admin, fecha_asignacion)
    if nuevo_id:
        return _json_ok({"idEstadio": nuevo_id})
    return _json_error(error or "No se pudo crear el estadio", 500)


@app.route("/sector", methods=["POST"])
def ruta_crear_sector():
    bloqueo = _requiere_admin()
    if bloqueo:
        return bloqueo
    datos = _input_payload()
    id_estadio = datos.get("idEstadio")
    codigo = (datos.get("codigo") or "").strip()
    capacidad = datos.get("capacidadMaxima")
    costo = datos.get("costoEntrada")
    if not id_estadio:
        return _json_error("Falta el ID del estadio", 400)
    if not codigo:
        return _json_error("Falta el código del sector", 400)
    if not capacidad:
        return _json_error("Falta la capacidad máxima del sector", 400)
    if costo is None:
        return _json_error("Falta el costo de entrada", 400)
    nuevo_id, error = crear_sector(id_estadio, codigo, capacidad, costo)
    if nuevo_id:
        return _json_ok({"idSector": nuevo_id})
    return _json_error(error or "No se pudo crear el sector", 500)


@app.route("/evento", methods=["POST"])
def ruta_crear_evento():
    bloqueo = _requiere_admin()
    if bloqueo:
        return bloqueo
    datos = _input_payload()
    nombre = (datos.get("nombreEvento") or "").strip()
    fecha = (datos.get("fecha") or "").strip()
    hora = (datos.get("hora") or "").strip()
    id_estadio = datos.get("idEstadio")
    email_admin = (datos.get("emailAdmin") or session.get("user_email") or "").strip()
    if not nombre:
        return _json_error("Falta el nombre del evento", 400)
    if not fecha:
        return _json_error("Falta la fecha del evento", 400)
    if not hora:
        return _json_error("Falta la hora del evento", 400)
    if not id_estadio:
        return _json_error("Falta el ID del estadio", 400)
    if not email_admin:
        return _json_error("Falta el email del administrador", 400)
    nuevo_id, error = crear_evento(nombre, fecha, hora, id_estadio, email_admin)
    if nuevo_id:
        return _json_ok({"idEvento": nuevo_id})
    return _json_error(error or "No se pudo crear el evento", 500)


@app.route("/evento/equipo", methods=["POST"])
def ruta_vincular_equipo():
    bloqueo = _requiere_admin()
    if bloqueo:
        return bloqueo
    datos = _input_payload()
    exito = vincular_equipo_evento(datos.get("idEvento"), datos.get("idEquipo"), datos.get("rol"))
    return _json_ok({"vinculado": exito}) if exito else _json_error("No se pudo vincular el equipo", 500)


@app.route("/evento/sector", methods=["POST"])
def ruta_habilitar_sector():
    bloqueo = _requiere_admin()
    if bloqueo:
        return bloqueo
    datos = _input_payload()
    exito = habilitar_sector_evento(datos.get("idEvento"), datos.get("idSector"))
    return _json_ok({"habilitado": exito}) if exito else _json_error("No se pudo habilitar el sector", 500)


@app.route("/eventos", methods=["GET"])
def ruta_listar_eventos():
    return _json_ok({"eventos": listar_eventos()})


@app.route("/estadios", methods=["GET"])
def ruta_listar_estadios():
    return _json_ok({"estadios": listar_estadios()})


@app.route("/sectores", methods=["GET"])
def ruta_listar_sectores():
    return _json_ok({"sectores": listar_sectores()})


@app.route("/vinculaciones", methods=["GET"])
def ruta_listar_vinculaciones():
    return _json_ok({"vinculaciones": listar_vinculaciones()})


@app.route("/eventos/<int:id_evento>/sectores", methods=["GET"])
def ruta_listar_sectores_evento(id_evento):
    return _json_ok({"sectores": listar_sectores_evento(id_evento)})


@app.route("/eventos/<int:id_evento>/funcionarios", methods=["GET"])
def ruta_listar_funcionarios_evento(id_evento):
    return _json_ok({"funcionarios": listar_funcionarios_evento(id_evento)})


@app.route("/estadios/<int:id_estadio>/codigos-disponibles", methods=["GET"])
def ruta_codigos_sector_disponibles(id_estadio):
    return _json_ok({"codigos": listar_codigos_sector_disponibles(id_estadio)})


@app.route("/eventos/<int:id_evento>/equipos-disponibles", methods=["GET"])
def ruta_equipos_disponibles_evento(id_evento):
    return _json_ok({"equipos": listar_equipos_disponibles_evento(id_evento)})


@app.route("/eventos/<int:id_evento>/sectores-disponibles", methods=["GET"])
def ruta_sectores_disponibles_evento(id_evento):
    return _json_ok({"sectores": listar_sectores_disponibles_evento(id_evento)})


@app.route("/eventos/<int:id_evento>/entradas-no-validadas", methods=["GET"])
def ruta_entradas_no_validadas_evento(id_evento):
    return _json_ok({"entradas": listar_entradas_no_validadas_por_evento(id_evento)})


@app.route("/eventos/<int:id_evento>/entradas-validadas", methods=["GET"])
def ruta_entradas_validadas_evento(id_evento):
    return _json_ok({"entradas": listar_entradas_validadas_por_evento(id_evento)})


@app.route("/equipos", methods=["GET"])
def ruta_listar_equipos():
    return _json_ok({"equipos": listar_equipos()})


@app.route("/usuarios/compradores", methods=["GET"])
def ruta_listar_compradores():
    bloqueo = _requiere_admin()
    if bloqueo:
        return bloqueo
    return _json_ok({"compradores": listar_compradores()})


@app.route("/comprar", methods=["POST"])
def procesar_compra():
    datos = _input_payload()
    if _es_admin_activo() and datos.get("emailComprador"):
        email_comprador = datos.get("emailComprador")
    else:
        email_comprador = session.get("user_email") or datos.get("emailComprador")
    cantidad = int(datos.get("cantidad", 0))

    if cantidad > 5:
        return _json_error("No puedes comprar más de 5 entradas en la misma transaccion.", 400)

    id_venta = registrar_venta_y_entradas(email_comprador, [{"id_evento": datos.get("idEvento"), "id_sector": datos.get("idSector"), "cantidad": cantidad}])
    if id_venta:
        return _json_ok({"compra": True, "idVenta": id_venta})
    return _json_error("Error en la compra: sector agotado o error de sistema.", 500)


@app.route("/compras/multiples", methods=["POST"])
def ruta_compra_multiple():
    datos = _input_payload()
    email_comprador = session.get("user_email") or datos.get("emailComprador")
    id_venta = registrar_venta_y_entradas(email_comprador, datos.get("items", []), datos.get("estado", "paga"))
    if id_venta:
        return _json_ok({"idVenta": id_venta})
    return _json_error("No se pudo registrar la compra múltiple", 500)


@app.route("/ventas/pendientes", methods=["GET"])
def ruta_ventas_pendientes():
    bloqueo = _requiere_admin()
    if bloqueo:
        return bloqueo
    return _json_ok({"ventas": listar_ventas_pendientes()})


@app.route("/venta/<int:id_venta>/confirmar-pedido", methods=["POST"])
def ruta_confirmar_pedido(id_venta):
    bloqueo = _requiere_admin()
    if bloqueo:
        return bloqueo
    exito, error = confirmar_pedido_venta(id_venta)
    if exito:
        return _json_ok({"confirmado": True})
    return _json_error(error or "No se pudo confirmar el pedido", 400)


@app.route("/venta/<int:id_venta>/confirmar-pago", methods=["POST"])
def ruta_confirmar_pago(id_venta):
    bloqueo = _requiere_admin()
    if bloqueo:
        return bloqueo
    exito, error = confirmar_pago_venta(id_venta)
    if exito:
        return _json_ok({"confirmada": True})
    return _json_error(error or "No se pudo confirmar el pago", 400)


@app.route("/usuario/<string:email>/compras", methods=["GET"])
def ruta_compras_usuario(email):
    return _json_ok({"compras": listar_compras_usuario(email)})


@app.route("/usuario/<string:email>/entradas", methods=["GET"])
def ruta_entradas_usuario(email):
    return _json_ok({"entradas": listar_entradas_usuario(email)})


@app.route("/usuario/<string:email>/transferencias", methods=["GET"])
def ruta_transferencias_usuario(email):
    return _json_ok({"transferencias": listar_transferencias_usuario(email)})


@app.route("/transferencia", methods=["POST"])
def ruta_solicitar_transferencia():
    datos = _input_payload()
    origen = (datos.get("emailOrigen") or "").strip()
    destino = (datos.get("emailDestino") or "").strip()
    ids_entrada = datos.get("idsEntrada", [])
    if isinstance(ids_entrada, (int, str)):
        ids_entrada = [int(ids_entrada)]
    if not isinstance(ids_entrada, list):
        return _json_error("Formato inválido de idsEntrada", 400)
    ids_entrada = [int(x) for x in ids_entrada if str(x).strip().isdigit()]
    if not origen:
        return _json_error("Falta el email de origen", 400)
    if not destino:
        return _json_error("Falta el email de destino", 400)
    if origen == destino:
        return _json_error("El origen y destino no pueden ser el mismo", 400)
    if not ids_entrada:
        return _json_error("Selecciona al menos una entrada para transferir", 400)
    ids, error = solicitar_transferencia(origen, destino, ids_entrada)
    if ids:
        return _json_ok({"idsTransferencia": ids, "cantidad": len(ids)})
    return _json_error(error or "No se pudo solicitar la transferencia", 500)


@app.route("/transferencia/<int:id_transferencia>", methods=["POST"])
def ruta_responder_transferencia(id_transferencia):
    datos = _input_payload()
    exito = responder_transferencia(id_transferencia, datos.get("estado"))
    return _json_ok({"actualizada": exito}) if exito else _json_error("No se pudo responder la transferencia", 500)


@app.route("/entrada/<int:id_entrada>/qr", methods=["POST"])
def ruta_registrar_qr(id_entrada):
    datos = _input_payload()
    nuevo_token = registrar_token_qr(
        id_entrada,
        datos.get("valor"),
        datos.get("tiempoVencimiento", 30),
    )
    return _json_ok({"idToken": nuevo_token}) if nuevo_token else _json_error("No se pudo registrar el token QR", 500)


@app.route("/entrada/<int:id_entrada>/qr", methods=["GET"])
def ruta_token_activo(id_entrada):
    return _json_ok({"token": obtener_token_activo(id_entrada)})


@app.route("/mi-entrada/<int:id_entrada>/qr", methods=["POST"])
def ruta_mi_qr(id_entrada):
    email = session.get("user_email")
    if not email:
        return _json_error("No has iniciado sesión", 401)
    entradas = listar_entradas_usuario(email)
    if not any(e["idEntrada"] == id_entrada for e in entradas):
        return _json_error("Esta entrada no te pertenece", 403)
    datos = _input_payload()
    nuevo_token = registrar_token_qr(
        id_entrada,
        datos.get("valor"),
        datos.get("tiempoVencimiento", 30),
    )
    if not nuevo_token:
        return _json_error("No se pudo registrar el token QR", 500)
    token = obtener_token_activo(id_entrada)
    return _json_ok({"idToken": nuevo_token, "token": token})


@app.route("/validar", methods=["POST"])
def ruta_validar_entrada():
    datos = _input_payload()
    email_func = datos.get("emailFuncionario")
    if email_func:
        asegurar_funcionario(email_func)
    exito, err = validar_entrada(datos.get("idToken"), datos.get("idDispositivo"), email_func)
    return _json_ok({"validada": exito}) if exito else _json_error(err or "No se pudo validar la entrada", 422)


@app.route("/funcionarios", methods=["GET"])
def ruta_listar_funcionarios():
    return _json_ok({"funcionarios": listar_funcionarios()})


@app.route("/eventos/<int:id_evento>/asignaciones", methods=["GET"])
def ruta_asignaciones_evento(id_evento):
    return _json_ok({"asignaciones": listar_asignaciones_evento(id_evento)})


@app.route("/asignacion", methods=["POST"])
def ruta_asignar_funcionario():
    bloqueo = _requiere_admin()
    if bloqueo:
        return bloqueo
    datos = _input_payload()
    id_evento = datos.get("idEvento")
    id_sector = datos.get("idSector")
    email = datos.get("emailFuncionario")
    if not id_evento or not id_sector or not email:
        return _json_error("Faltan datos: idEvento, idSector, emailFuncionario", 400)
    exito, error = asignar_funcionario_sector(id_evento, id_sector, email)
    if exito:
        return _json_ok({"asignado": True})
    return _json_error(error or "No se pudo asignar el funcionario", 500)


@app.route("/asignacion", methods=["DELETE"])
def ruta_eliminar_asignacion():
    bloqueo = _requiere_admin()
    if bloqueo:
        return bloqueo
    datos = _input_payload()
    exito, error = eliminar_asignacion_funcionario(
        datos.get("idEvento"), datos.get("idSector"), datos.get("emailFuncionario"),
    )
    if exito:
        return _json_ok({"eliminado": True})
    return _json_error(error or "No se pudo eliminar la asignación", 500)


@app.route("/funcionario/<string:email>/dispositivos", methods=["GET"])
def ruta_dispositivos_funcionario(email):
    return _json_ok({"dispositivos": listar_dispositivos_por_funcionario(email)})


@app.route("/funcionario/<string:email>/asignaciones", methods=["GET"])
def ruta_asignaciones_funcionario(email):
    return _json_ok({"asignaciones": listar_asignaciones_funcionario(email)})


@app.route("/funcionario/<string:email>/evento/<int:id_evento>/cobertura", methods=["GET"])
def ruta_cobertura_funcionario(email, id_evento):
    return _json_ok({"cobertura": cobertura_funcionario_evento(id_evento, email)})


@app.route("/eventos/<int:id_evento>/cobertura", methods=["GET"])
def ruta_cobertura_evento(id_evento):
    return _json_ok({"cobertura": cobertura_evento_completa(id_evento)})


@app.route("/ranking/eventos", methods=["GET"])
def ruta_ranking_eventos():
    limite = int(request.args.get("limite", 10))
    return _json_ok({"ranking": ranking_eventos_mas_vendidos(limite)})


@app.route("/ranking/compradores", methods=["GET"])
def ruta_ranking_compradores():
    limite = int(request.args.get("limite", 10))
    return _json_ok({"ranking": ranking_mayores_compradores(limite)})


@app.route("/usuarios/pendientes", methods=["GET"])
def ruta_usuarios_pendientes():
    bloqueo = _requiere_admin()
    if bloqueo:
        return bloqueo
    return _json_ok({"pendientes": listar_pendientes_validacion()})


@app.route("/usuarios/<email>/verificar", methods=["POST"])
def ruta_verificar_usuario(email):
    bloqueo = _requiere_admin()
    if bloqueo:
        return bloqueo
    datos = _input_payload()
    nuevo_estado = datos.get("estado")
    if nuevo_estado not in ("verificado", "rechazado"):
        return _json_error("Estado inválido. Use 'verificado' o 'rechazado'.", 400)
    exito = actualizar_estado_verificacion(email, nuevo_estado)
    return _json_ok({"actualizado": exito}) if exito else _json_error("No se pudo actualizar el estado", 500)


@app.route("/usuario/<email>/datos", methods=["GET"])
def ruta_obtener_usuario(email):
    bloqueo = _requiere_admin()
    if bloqueo:
        return bloqueo
    usuario = obtener_usuario_por_email(email)
    if not usuario:
        return _json_error("Usuario no encontrado", 404)
    telefonos = obtener_telefonos_usuario(email)
    usuario["telefonos"] = telefonos
    return _json_ok(usuario)


@app.route("/usuario/<email>/datos", methods=["PUT"])
def ruta_actualizar_usuario(email):
    bloqueo = _requiere_admin()
    if bloqueo:
        return bloqueo
    datos = _input_payload()
    exito, error = actualizar_usuario(email, datos)
    if not exito:
        return _json_error(error or "Error al actualizar usuario", 500)
    if "telefonos" in datos:
        actualizar_telefonos_usuario(email, datos["telefonos"])
    return _json_ok({"actualizado": True})


@app.route("/usuario/<email>/roles", methods=["POST"])
def ruta_actualizar_roles(email):
    bloqueo = _requiere_admin()
    if bloqueo:
        return bloqueo
    datos = _input_payload()
    exito, error = actualizar_roles_usuario(email, datos)
    if exito:
        return _json_ok({"actualizado": True})
    return _json_error(error or "No se pudieron actualizar los roles", 500)


if __name__ == "__main__":
    app.run(debug=True)