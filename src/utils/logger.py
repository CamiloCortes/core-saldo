import logging
from datetime import datetime, timezone
from pythonjsonlogger import jsonlogger

logger = logging.getLogger("core-saldo")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter(
        "%(timestamp)s %(level)s %(service)s %(traceId)s %(sessionId)s %(operation)s %(message)s %(status)s %(durationMs)s %(httpStatus)s %(errorCode)s"
    )
    handler.setFormatter(formatter)
    handler.setLevel(logging.INFO)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False


def log_event(level: str, message: str = None, **kwargs):
    extra = {
        "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
        "level": level.upper(),
        "service": "core-transferencias",
        "traceId": kwargs.get("traceId"),
        "sessionId": kwargs.get("sessionId"),
        "operation": kwargs.get("operation"),
        "status": kwargs.get("status"),
        "durationMs": kwargs.get("durationMs"),
        "httpStatus": kwargs.get("httpStatus"),
        "errorCode": kwargs.get("errorCode"),
    }

    extra.pop("password", None)
    extra.pop("password_hash", None)

    log_method = getattr(logger, level.lower(), logger.info)
    log_method(message or "", extra=extra)
