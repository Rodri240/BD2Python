"""
Database module - Centraliza todas las funciones de acceso a datos.

Importa funciones de los diferentes módulos para mantener compatibilidad
con el código existente.
"""

# Usuarios y Autenticación
from .usuarios import (
    autenticar_usuario,
    registrar_usuario_general,
    registrar_usuario_admin,
    registrar_funcionario_validacion,
    listar_compradores,
    listar_pendientes_validacion,
    actualizar_estado_verificacion,
    asegurar_funcionario,
    listar_funcionarios,
    listar_asignaciones_evento,
    listar_asignaciones_funcionario,
    asignar_funcionario_sector,
    eliminar_asignacion_funcionario,
    obtener_usuario_por_email,
    obtener_telefonos_usuario,
    actualizar_usuario,
    actualizar_telefonos_usuario,
    actualizar_roles_usuario,
)

# Infraestructura
from .infraestructura import (
    crear_estadio,
    crear_sector,
    listar_estadios,
    listar_sectores,
    listar_codigos_sector_disponibles,
)

# Eventos
from .eventos import (
    crear_evento,
    vincular_equipo_evento,
    habilitar_sector_evento,
    listar_eventos,
    listar_vinculaciones,
    listar_equipos_disponibles_evento,
    listar_sectores_disponibles_evento,
    listar_sectores_evento,
    listar_entradas_no_validadas_por_evento,
    listar_entradas_validadas_por_evento,
)

# Equipos
from .equipos import (
    listar_equipos,
)

# Dispositivos
from .dispositivos import (
    registrar_dispositivo,
    listar_dispositivos_por_funcionario,
)

# Compras
from .compras import (
    registrar_venta_y_entradas,
    ejecutar_transaccion_venta,
    listar_compras_usuario,
    listar_entradas_usuario,
)

# Transferencias
from .transferencias import (
    listar_transferencias_usuario,
    solicitar_transferencia,
    responder_transferencia,
)

# Validación
from .validacion import (
    registrar_token_qr,
    obtener_token_activo,
    validar_entrada,
)

# Reportes
from .reportes import (
    ranking_eventos_mas_vendidos,
    ranking_mayores_compradores,
    cobertura_funcionario_evento,
    cobertura_evento_completa,
    listar_funcionarios_evento,
)

# Utilities
from .utils import (
    interpretar_error_db,
)

__all__ = [
    # Usuarios y Autenticación
    "autenticar_usuario",
    "registrar_usuario_general",
    "registrar_usuario_admin",
    "registrar_funcionario_validacion",
    "listar_compradores",
    "listar_pendientes_validacion",
    "actualizar_estado_verificacion",
    "asegurar_funcionario",
    "listar_funcionarios",
    "listar_asignaciones_evento",
    "listar_asignaciones_funcionario",
    "asignar_funcionario_sector",
    "eliminar_asignacion_funcionario",
    "obtener_usuario_por_email",
    "obtener_telefonos_usuario",
    "actualizar_usuario",
    "actualizar_telefonos_usuario",
    "actualizar_roles_usuario",
    # Infraestructura
    "crear_estadio",
    "crear_sector",
    "listar_estadios",
    "listar_sectores",
    "listar_codigos_sector_disponibles",
    # Eventos
    "crear_evento",
    "vincular_equipo_evento",
    "habilitar_sector_evento",
    "listar_eventos",
    "listar_vinculaciones",
    "listar_equipos_disponibles_evento",
    "listar_sectores_disponibles_evento",
    "listar_sectores_evento",
    # Equipos
    "listar_equipos",
    # Dispositivos
    "registrar_dispositivo",
    "listar_dispositivos_por_funcionario",
    # Compras
    "registrar_venta_y_entradas",
    "ejecutar_transaccion_venta",
    "listar_compras_usuario",
    "listar_entradas_usuario",
    # Transferencias
    "listar_transferencias_usuario",
    "solicitar_transferencia",
    "responder_transferencia",
    # Validación
    "registrar_token_qr",
    "obtener_token_activo",
    "validar_entrada",
    # Reportes
    "ranking_eventos_mas_vendidos",
    "ranking_mayores_compradores",
    "cobertura_funcionario_evento",
    "cobertura_evento_completa",
    "listar_funcionarios_evento",
    # Utilities
    "interpretar_error_db",
]
