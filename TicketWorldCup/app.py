from datetime import date, datetime, time, timedelta
from decimal import Decimal

from flask import Flask, jsonify, redirect, render_template, request, session, url_for

try:
    from Database.querys import (
        autenticar_usuario,
        registrar_usuario_general,
        registrar_usuario_admin,
        registrar_funcionario_validacion,
        registrar_dispositivo,
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
        listar_compradores,
        registrar_venta_y_entradas,
        ejecutar_transaccion_venta,
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
    )
except ImportError:
    from Database.querys import (
        autenticar_usuario,
        registrar_usuario_general,
        registrar_usuario_admin,
        registrar_funcionario_validacion,
        registrar_dispositivo,
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
        listar_compradores,
        registrar_venta_y_entradas,
        ejecutar_transaccion_venta,
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


@app.route("/", methods=["GET"])
def index():
    if not session.get("user_email"):
        return redirect(url_for("login"))
    return render_template(
        "index.html",
        session_email=session.get("user_email"),
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
    return render_template("registro.html", session_email=session.get("user_email"))


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
    return render_template("validacion.html", session_email=session.get("user_email"))


@app.route("/consultas", methods=["GET"])
def consultas():
    return render_template("consultas.html", session_email=session.get("user_email"))


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
    nuevo_id = registrar_dispositivo(datos.get("dirMAC"), datos.get("emailFuncionario"))
    return _json_ok({"idDispositivo": nuevo_id}) if nuevo_id else _json_error("No se pudo registrar el dispositivo", 500)


@app.route("/estadio", methods=["POST"])
def ruta_crear_estadio():
    bloqueo = _requiere_admin()
    if bloqueo:
        return bloqueo
    datos = _input_payload()
    email_admin = (datos.get("emailAdmin") or session.get("user_email") or "").strip()
    if not email_admin:
        return _json_error("Falta el email del administrador", 400)
    nuevo_id = crear_estadio(
        datos.get("nombre"),
        datos.get("pais"),
        datos.get("ciudad"),
        email_admin,
        datos.get("fechaAsignacion"),
    )
    return _json_ok({"idEstadio": nuevo_id}) if nuevo_id else _json_error("No se pudo crear el estadio", 500)


@app.route("/sector", methods=["POST"])
def ruta_crear_sector():
    bloqueo = _requiere_admin()
    if bloqueo:
        return bloqueo
    datos = _input_payload()
    nuevo_id = crear_sector(
        datos.get("idEstadio"),
        datos.get("codigo"),
        datos.get("capacidadMaxima"),
        datos.get("costoEntrada"),
    )
    return _json_ok({"idSector": nuevo_id}) if nuevo_id else _json_error("No se pudo crear el sector", 500)


@app.route("/evento", methods=["POST"])
def ruta_crear_evento():
    bloqueo = _requiere_admin()
    if bloqueo:
        return bloqueo
    datos = _input_payload()
    email_admin = (datos.get("emailAdmin") or session.get("user_email") or "").strip()
    if not email_admin:
        return _json_error("Falta el email del administrador", 400)
    nuevo_id = crear_evento(
        datos.get("nombreEvento"),
        datos.get("fecha"),
        datos.get("hora"),
        datos.get("idEstadio"),
        email_admin,
    )
    return _json_ok({"idEvento": nuevo_id}) if nuevo_id else _json_error("No se pudo crear el evento", 500)


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


@app.route("/estadios/<int:id_estadio>/codigos-disponibles", methods=["GET"])
def ruta_codigos_sector_disponibles(id_estadio):
    return _json_ok({"codigos": listar_codigos_sector_disponibles(id_estadio)})


@app.route("/eventos/<int:id_evento>/equipos-disponibles", methods=["GET"])
def ruta_equipos_disponibles_evento(id_evento):
    return _json_ok({"equipos": listar_equipos_disponibles_evento(id_evento)})


@app.route("/eventos/<int:id_evento>/sectores-disponibles", methods=["GET"])
def ruta_sectores_disponibles_evento(id_evento):
    return _json_ok({"sectores": listar_sectores_disponibles_evento(id_evento)})


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
    resultado = solicitar_transferencia(
        datos.get("idEntrada"),
        datos.get("emailOrigen"),
        datos.get("emailDestino"),
    )
    if resultado:
        return _json_ok({"idTransferencia": resultado})
    return _json_error("No se pudo solicitar la transferencia", 500)


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


@app.route("/validar", methods=["POST"])
def ruta_validar_entrada():
    datos = _input_payload()
    exito = validar_entrada(datos.get("idToken"), datos.get("idDispositivo"), datos.get("emailFuncionario"))
    return _json_ok({"validada": exito}) if exito else _json_error("No se pudo validar la entrada", 500)


@app.route("/funcionario/<string:email>/evento/<int:id_evento>/cobertura", methods=["GET"])
def ruta_cobertura_funcionario(email, id_evento):
    return _json_ok({"cobertura": cobertura_funcionario_evento(id_evento, email)})


@app.route("/ranking/eventos", methods=["GET"])
def ruta_ranking_eventos():
    limite = int(request.args.get("limite", 10))
    return _json_ok({"ranking": ranking_eventos_mas_vendidos(limite)})


@app.route("/ranking/compradores", methods=["GET"])
def ruta_ranking_compradores():
    limite = int(request.args.get("limite", 10))
    return _json_ok({"ranking": ranking_mayores_compradores(limite)})


if __name__ == "__main__":
    app.run(debug=True)