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
)

# Equipos
from .equipos import (
    listar_equipos,
)

# Dispositivos
from .dispositivos import (
    registrar_dispositivo,
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
)

__all__ = [
    # Usuarios y Autenticación
    "autenticar_usuario",
    "registrar_usuario_general",
    "registrar_usuario_admin",
    "registrar_funcionario_validacion",
    "listar_compradores",
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
]
