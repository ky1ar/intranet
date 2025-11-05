# Entorno de Desarrollo - Intranet & Registro (Flask + Alpine.js + Nginx + Docker)

## Descripción General

Este entorno permite ejecutar en **modo desarrollo (dev)** el ecosistema compuesto por:

- **Backend (`api-dev`)**: API Flask con `Flask-SocketIO`, `SQLAlchemy`, `JWT`, `Redis` y arquitectura modular por Blueprints.
- **Frontends (`intranet-dev` y `registro-dev`)**: SPA estáticas servidas por `nginx:alpine` y desarrolladas con **Alpine.js**.
- **Redis (`redis-dev`)**: Motor de caché en memoria y soporte para sesiones/socket.

---

## Entorno de Ejecución

- **Sistema Operativo:** Windows 10/11  
- **Terminal:** PowerShell  
- **Contenedores:** Docker Desktop  
- **Opcional:** Python 3.11 + pip (para ejecutar backend sin Docker)

---

## Variables de Entorno (Archivo `.env.dev`)

Ubicación: `backend/.env.dev`

| Variable | Descripción | Ejemplo |
|-----------|-------------|----------|
| `ENV` | Entorno de ejecución | `dev` |
| `API_HOST` | Host de la API | `0.0.0.0` |
| `API_PORT` | Puerto de la API | `5010` |
| `DATABASE_URI` | Conexión MySQL (remota) | `mysql+pymysql://user:pass@host/db` |
| `REDIS_URL` | Conexión a Redis | `redis://:150723@redis_dev:6379/0` |
| `JWT_SECRET_KEY` | Clave JWT | `clave_segura_123` |
| `BASE_URL`, `APISNET_URL`, `APIPERU_URL`, etc. | Endpoints externos | *(depende del entorno)* |

> El archivo `.env.dev` es cargado automáticamente por `dotenv` en `config.py`.

---

## Ejecución con Docker (Recomendado)

### 1️ Posicionarse en el directorio del proyecto
```powershell
Set-Location C:\Users\kebos\Intranet\intranet
```

### 2️ Exportar variables del entorno
```powershell
$env:ENV = "dev"
$env:API_PORT = "5010"
```

### 3️ Construir y levantar todos los servicios
```powershell
docker compose -f docker-compose.dev.yml up --build -d
```

### 4️ Verificar que los contenedores estén activos
```powershell
docker ps
```
Deberías ver:

| CONTAINER NAME | STATUS | PORTS |
|-----------------|---------|--------|
| api-dev         | Up | 5010→5010 |
| redis-dev       | Up | 6379→6379 |
| intranet-dev    | Up | 7010→80 |
| registro-dev    | Up | 7011→80 |

---

## Verificación del Backend

Ejecuta:
```powershell
Invoke-WebRequest http://localhost:5010/dev/
```

Respuesta esperada:
```json
{"status":"ok","env":"dev"}
```

---

## Acceso a los Frontends

| Servicio | URL | Descripción |
|-----------|------|-------------|
| Intranet | [http://localhost:7010](http://localhost:7010) | Interfaz principal (Alpine.js + Nginx) |
| Registro | [http://localhost:7011](http://localhost:7011) | Portal de registro de usuarios |

---

## Configuración del API en Frontends

Por defecto los frontends apuntan a producción (`https://api.krear3d.com`).  
Para trabajar en local, reemplaza la base de la API en los `main.js`:

```powershell
((Get-Content intranet\intranet\static\js\main.js -Raw) -replace "https://api.krear3d.com","http://localhost:5010") | Set-Content intranet\intranet\static\js\main.js

((Get-Content registro\static\js\main.js -Raw) -replace "https://api.krear3d.com","http://localhost:5010") | Set-Content registro\static\js\main.js
```

Luego reinicia los servicios:
```powershell
docker compose -f docker-compose.dev.yml restart api-dev intranet-dev registro-dev
```

---

## 📂 Estructura de Carpetas (Resumen)

```
intranet/
├── backend/
│   ├── application/
│   │   ├── controllers/
│   │   ├── services/
│   │   ├── repositories/
│   │   ├── proxy/
│   │   ├── models/
│   │   ├── *_routes.py
│   │   └── __init__.py
│   ├── config.py
│   ├── main.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.dev
│
├── intranet/
│   ├── index.html
│   ├── static/js/main.js
│   ├── views/*.html
│   ├── nginx.conf
│   └── Dockerfile
│
├── registro/
│   ├── index.html
│   ├── static/js/main.js
│   ├── nginx.conf
│   └── Dockerfile
│
└── docker-compose.dev.yml
```

---

## Comandos Útiles (Docker)

| Acción | Comando |
|--------|----------|
| Ver logs del backend | `docker compose -f docker-compose.dev.yml logs -f api-dev` |
| Reiniciar backend | `docker compose -f docker-compose.dev.yml restart api-dev` |
| Detener todos los servicios | `docker compose -f docker-compose.dev.yml down` |
| Vaciar caché Redis | `Invoke-WebRequest http://localhost:5010/dev/flush-redis` |

---

PARA CORRER EL FORNT DSESDE EL DOCJKER:
cd c:\Users\kebos\Intranet ; $env:ENV='dev'; $env:API_PORT='5010'; docker compose -f intranet/docker-compose.dev.yml up -d