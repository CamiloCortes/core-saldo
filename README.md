# Core Saldo

Servicio responsable de consultar saldo de cuentas y obtener movimientos (débitos y créditos) de los usuarios..

## Responsabilidad

- Consulta de saldo actual de una cuenta a partir del `userId`
- Consulta del histórico de movimientos del usuario (últimos 50)
- Validación de sesión cifrada en Redis (zero-trust)
- Validación de coincidencia entre el `userId` de la sesión y el del body

No persiste datos directamente: solo lee de las tablas `cuentas` y `movimientos` que mantiene Core Transferencias.

## Stack tecnológico

- Python 3.12
- FastAPI
- asyncpg (driver PostgreSQL asíncrono)
- redis.asyncio (driver Redis asíncrono)
- Pydantic 2 (validación y schemas)
- cryptography (AES-256-GCM para descifrado de sesiones)
- python-json-logger (logs estructurados)

## Estructura del proyecto
core-saldo/
├── README.md
├── requirements.txt
├── .env.example
└── src/
├── main.py
├── config/
│   ├── database.py       (pool asyncpg)
│   └── redis.py          (cliente Redis async)
├── middlewares/
│   ├── trace_middleware.py    (propagación de traceId)
│   └── session_middleware.py  (validación de sesión)
├── schemas/
│   └── balance_schemas.py     (Pydantic schemas)
├── repositories/
│   └── balance_repository.py  (queries SQL)
├── services/
│   └── balance_service.py     (lógica de negocio)
├── routers/
│   └── balance.py             (endpoints REST)
└── utils/
├── logger.py              (logs estructurados JSON)
└── crypto.py              (descifrado AES-256-GCM)

## Requisitos previos

- Python 3.12
- PostgreSQL 17 corriendo (compartido con los demás servicios)
- Redis 7 corriendo (compartido con los demás servicios)
- Tablas `usuarios`, `cuentas` y `movimientos` ya creadas
- Sesiones cifradas activas en Redis (creadas por el Auth Service)

## Instalación

### 1. Crear entorno virtual

```bash
cd core-saldo
python -m venv venv

# Windows
.\venv\Scripts\Activate.ps1

# Linux/Mac
source venv/bin/activate
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Configurar variables de entorno

Copia `.env.example` a `.env` y completa los valores:

```env
PORT=8002

POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=dbPruebaBackend
POSTGRES_USER=ADMBKN
POSTGRES_PASSWORD=admin123

REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

SESSION_ENCRYPTION_KEY=
```

**Importante:** la `SESSION_ENCRYPTION_KEY` debe ser **exactamente la misma** que la del Auth Service y demás Cores. Si difiere, no podrá descifrar las sesiones generadas por el Auth Service.

### 4. Ejecutar el servicio

```bash
uvicorn src.main:app --reload --port 8002
```

El servicio queda disponible en `http://localhost:8002`. Verás en consola:
Pool de PostgreSQL inicializado
INFO:     Uvicorn running on http://0.0.0.0:8002

## Endpoints

Todos los endpoints requieren los headers:
- `x-session-id`: id de sesión activa en Redis
- `x-trace-id` (opcional): identificador de trazabilidad

### POST /core2/balance

Consulta el saldo de la cuenta del usuario.

**Request body:**
```json
{
  "userId": "uuid-del-usuario"
}
```

**Response 200:**
```json
{
  "numeroCuenta": "****0001",
  "saldo": "450000.00",
  "estado": "ACTIVA"
}
```

### POST /core2/movements

Consulta los últimos 50 movimientos del usuario (débitos y créditos), ordenados por fecha descendente.

**Request body:**
```json
{
  "userId": "uuid-del-usuario"
}
```

**Response 200:**
```json
{
  "movimientos": [
    {
      "movimientoId": "uuid-...",
      "tipo": "DEBITO",
      "monto": "25000.00",
      "saldoAnterior": "475000.00",
      "saldoPosterior": "450000.00",
      "descripcion": "Transferencia enviada",
      "fecha": "2026-05-19T10:30:00"
    }
  ],
  "total": 1
}
```

### GET /docs

Documentación Swagger interactiva generada automáticamente por FastAPI.

## Códigos de error

| Status | errorCode | Descripción |
|--------|-----------|-------------|
| 401 | SESSION_MISSING | Header `x-session-id` no enviado |
| 401 | SESSION_EXPIRED | Sesión expirada o inexistente en Redis |
| 401 | SESSION_INVALID | Sesión cifrada corrupta |
| 503 | REDIS_ERROR | Error consultando Redis |
| 403 | USER_MISMATCH | El `userId` del body no coincide con el de la sesión |
| 404 | ACCOUNT_NOT_FOUND | El usuario no tiene cuenta asociada |
| 403 | ACCOUNT_INACTIVE | La cuenta del usuario no está activa |

## Decisiones técnicas

### Privacidad: número de cuenta enmascarado

El `numeroCuenta` se retorna como `****0001` (solo los últimos 4 dígitos). El número completo solo se usa internamente en la base de datos.

### Validación zero-trust de sesión

El middleware `require_session` (en `middlewares/session_middleware.py`) consulta Redis directamente para validar la sesión, sin confiar en lo que diga el Orchestrator. Si el Orchestrator fuera comprometido, este servicio seguiría protegido.

### Validación adicional de coincidencia userId

Después de validar la sesión, el router verifica que el `userId` del body coincida con el `userId` de la sesión descifrada. Esto previene que alguien con una sesión válida consulte datos de otro usuario.

### Límite de 50 movimientos por consulta

Para evitar respuestas con miles de registros en cuentas activas, el endpoint `/movements` retorna los últimos 50 movimientos. La paginación con cursor queda como mejora pendiente.

### Decimal en lugar de float para montos

Todos los valores monetarios usan `Decimal` de Python, nunca `float`. Esto preserva la precisión financiera.

### Logs estructurados con traceId propagado

Todos los logs salen en formato JSON con los campos definidos en el formato común del proyecto, incluyendo el `traceId` propagado desde el Orchestrator. Esto permite rastrear una operación completa a través de todos los servicios.

## Mejoras pendientes

- Paginación con cursor en `/movements`
- Filtros por tipo (DEBITO/CREDITO), rango de fechas y monto en `/movements`
- Cache de saldo con invalidación tras transferencias
- Health check de PostgreSQL y Redis en `/health`
- Tests unitarios completos