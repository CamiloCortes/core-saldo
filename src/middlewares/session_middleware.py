from fastapi import Request, HTTPException
from src.config.redis import redis_client
from src.utils.crypto import decrypt
from src.utils.logger import log_event


async def require_session(request: Request) -> dict:
    session_id = request.headers.get("x-session-id")

    if not session_id:
        raise HTTPException(
            status_code=401,
            detail={"errorCode": "SESSION_MISSING", "message": "SessionId requerido"}
        )

    try:
        encrypted = await redis_client.get(f"session:{session_id}")
    except Exception as e:
        log_event(
            "error",
            message="Error consultando Redis",
            traceId=getattr(request.state, "trace_id", None),
            errorCode="REDIS_ERROR"
        )
        raise HTTPException(
            status_code=503,
            detail={"errorCode": "REDIS_ERROR", "message": "Error del servicio"}
        )

    if not encrypted:
        log_event(
            "warn",
            message="Sesión expirada o inexistente",
            traceId=getattr(request.state, "trace_id", None),
            sessionId=session_id,
            operation="VALIDATE_SESSION",
            status="ERROR",
            httpStatus=401,
            errorCode="SESSION_EXPIRED"
        )
        raise HTTPException(
            status_code=401,
            detail={"errorCode": "SESSION_EXPIRED", "message": "Sesión expirada o inválida"}
        )

    try:
        session_data = decrypt(encrypted)
    except Exception:
        raise HTTPException(
            status_code=401,
            detail={"errorCode": "SESSION_INVALID", "message": "Sesión corrupta"}
        )

    request.state.user = session_data
    request.state.session_id = session_id

    return session_data
