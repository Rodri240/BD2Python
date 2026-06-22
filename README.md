# TicketWorldCup

Sistema de venta y validación de entradas para el Mundial de Fútbol 2026.

---

## Instructivo: Cómo ejecutar la app desde cero

### 1. Requisitos previos

- **Python 3.10+** instalado


### 2. Clonar e ingresar al proyecto

```bash
git clone <repo-url> BD2Python
cd BD2Python/TicketWorldCup
```

### 3. Crear y activar un entorno virtual

```bash
python -m venv venv

ejecutar ./venv/Scripts/activate    
```

### 4. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 5. Configurar variables de entorno

Crear un archivo `.env` en la carpeta `TicketWorldCup/` con el siguiente contenido:

```env
DB_HOST=
DB_USER=
DB_PASSWORD=
DB_NAME=
DB_PORT=
```


### 6. Ejecutar la aplicación

```bash
python app.py
```


### 7. Acceder a la aplicación

Abrir en el navegador 

**Usuarios de prueba incluidos en los datos semilla (`DDL OBL2 .SQL`):**

| Email | Contraseña | Rol |
|---|---|---|
| admin.usa@fifa.com | adminpass | Administrador (USA) |
| admin.mex@fifa.com | password123 | Administrador (México) |
| func.est1@fifa.com | password123 | Funcionario |
| func.est2@fifa.com | password123 | Funcionario |
| juan.perez@gmail.com | password123 | General |
| maria.garcia@gmail.com | password123 | General |
| carlos.lopez@gmail.com | password123 | General |
| ana.martinez@gmail.com | password123 | General |
| pedro.rodriguez@gmail.com | password123 | General |

> Para más detalles sobre los datos de prueba (estadios, eventos, entradas, transferencias, etc.), revisar el script `DDL OBL2 .SQL`.

---

