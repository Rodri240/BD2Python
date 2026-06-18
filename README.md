# Database Module - Estructura de Queries

Este módulo contiene todas las funciones de acceso a la base de datos, organizadas por funcionalidad.

## Estructura de Archivos

### 📂 Organización de Módulos

```
Database/
├── __init__.py                 # Punto de entrada - importa todas las funciones
├── connection.py               # Gestión de conexión a la BD
├── utils.py                    # Funciones auxiliares y helpers
├── usuarios.py                 # Autenticación y gestión de usuarios
├── infraestructura.py          # Estadios y Sectores
├── eventos.py                  # Eventos y vinculaciones
├── equipos.py                  # Listado de equipos
├── dispositivos.py             # Dispositivos de validación
├── compras.py                  # Ventas, compras y entradas
├── transferencias.py           # Transferencia de entradas entre usuarios
├── validacion.py               # Validación de entradas con QR
└── reportes.py                 # Reportes y análisis
```

## Descripción de Cada Módulo

### 📋 `connection.py`
**Gestión de conexiones a la base de datos**
- Configura y mantiene las conexiones con MySQL
- Punto central para obtener cursores de la BD

### 🛠️ `utils.py`
**Funciones auxiliares comunes**
- `normalizar_items_venta()` - Agrupa items de compra por evento/sector
- `obtener_password_hash()` - Genera hash SHA-256 de contraseñas
- `obtener_tasa_comision_actual()` - Obtiene tasa de comisión vigente

### 👥 `usuarios.py`
**Autenticación y gestión de usuarios**
- `autenticar_usuario()` - Valida credenciales
- `registrar_usuario_general()` - Registra compradores
- `registrar_usuario_admin()` - Registra administradores
- `registrar_funcionario_validacion()` - Registra funcionarios
- `listar_compradores()` - Lista todos los usuarios generales

### 🏟️ `infraestructura.py`
**Gestión de infraestructura (Estadios y Sectores)**

**Estadios:**
- `crear_estadio()` - Crea un nuevo estadio
- `listar_estadios()` - Lista todos los estadios

**Sectores:**
- `crear_sector()` - Crea un sector dentro de un estadio
- `listar_sectores()` - Lista todos los sectores
- `listar_codigos_sector_disponibles()` - Códigos libres (A, B, C, D)

### 🎪 `eventos.py`
**Gestión de eventos y vinculaciones**

**Eventos:**
- `crear_evento()` - Crea un nuevo evento
- `listar_eventos()` - Lista eventos con detalles
- `listar_sectores_evento()` - Sectores habilitados en un evento

**Vinculaciones:**
- `vincular_equipo_evento()` - Asigna equipos a eventos
- `habilitar_sector_evento()` - Habilita sectores para un evento
- `listar_vinculaciones()` - Todos los equipos y sectores vinculados

**Disponibilidad:**
- `listar_equipos_disponibles_evento()` - Equipos sin asignar
- `listar_sectores_disponibles_evento()` - Sectores sin habilitar

### ⚽ `equipos.py`
**Gestión de equipos**
- `listar_equipos()` - Lista todos los equipos disponibles

### 🔧 `dispositivos.py`
**Dispositivos de validación**
- `registrar_dispositivo()` - Registra dispositivo para validar entradas

### 🛒 `compras.py`
**Compras, ventas y entradas**

**Ventas:**
- `registrar_venta_y_entradas()` - Realiza una venta completa
- `ejecutar_transaccion_venta()` - Venta simplificada (1 evento/sector)
- `listar_compras_usuario()` - Historial de compras de un usuario

**Entradas:**
- `listar_entradas_usuario()` - Entradas activas del usuario

### 🔄 `transferencias.py`
**Transferencia de entradas entre usuarios**
- `solicitar_transferencia()` - Solicita transferir una entrada
- `responder_transferencia()` - Acepta o rechaza una transferencia
- `listar_transferencias_usuario()` - Historial de transferencias

### ✅ `validacion.py`
**Validación de entradas con QR**
- `registrar_token_qr()` - Genera token QR para una entrada
- `obtener_token_activo()` - Obtiene token válido y activo
- `validar_entrada()` - Valida una entrada usando QR

### 📊 `reportes.py`
**Reportes y análisis**
- `ranking_eventos_mas_vendidos()` - Top eventos por entradas vendidas
- `ranking_mayores_compradores()` - Top compradores por gasto
- `cobertura_funcionario_evento()` - Reporte de asistencia de funcionarios

---

## Cómo Importar

### Desde otro módulo de la aplicación:
```python
from Database import autenticar_usuario, listar_eventos
```

### Desde la carpeta Database:
```python
# Para importar utilidades
from .utils import normalizar_items_venta
# Para importar de un módulo específico
from .usuarios import autenticar_usuario
```

## Patrones de Uso

### Patrón de Transacción
```python
conn = get_db_connection()
cursor = conn.cursor()
try:
    conn.start_transaction()
    # ... operaciones ...
    conn.commit()
except Exception as e:
    conn.rollback()
finally:
    cursor.close()
    conn.close()
```

### Patrón de Lectura
```python
conn = get_db_connection()
cursor = conn.cursor(dictionary=True)
try:
    cursor.execute(sql, params)
    return cursor.fetchall()
finally:
    cursor.close()
    conn.close()
```

---

## Notas Importantes

- ✅ Las contraseñas se almacenan con hash SHA-256
- ✅ Las ventas pueden incluir hasta 5 entradas por transacción
- ✅ Las entradas pueden transferirse máximo 3 veces
- ✅ Los tokens QR vencen según el tiempo configurado
- ✅ Las transacciones usan `FOR UPDATE` para evitar condiciones de carrera

---

*Última actualización: 2026-06-18*
