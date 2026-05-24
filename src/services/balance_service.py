from typing import Dict, Optional

from fastapi import HTTPException

from src.repositories import balance_repository
from src.utils.logger import log_event


async def get_balance(user_id: str, trace_id: Optional[str] = None) -> Dict:
    cuenta = await balance_repository.find_balance_by_user_id(user_id)

    if not cuenta:
        log_event(
            "warning",
            "Cuenta no encontrada para el usuario",
            traceId=trace_id,
            operation="balance.get",
            status="ERROR",
            httpStatus=404,
            errorCode="ACCOUNT_NOT_FOUND",
        )
        raise HTTPException(
            status_code=404,
            detail={
                "errorCode": "ACCOUNT_NOT_FOUND",
                "message": "Cuenta no encontrada",
            },
        )

    if cuenta.get("estado") != "ACTIVA":
        log_event(
            "warning",
            "Cuenta inactiva al consultar saldo",
            traceId=trace_id,
            operation="balance.get",
            status="ERROR",
            httpStatus=403,
            errorCode="ACCOUNT_INACTIVE",
        )
        raise HTTPException(
            status_code=403,
            detail={
                "errorCode": "ACCOUNT_INACTIVE",
                "message": "Cuenta inactiva",
            },
        )

    log_event(
        "info",
        "Saldo consultado exitosamente",
        traceId=trace_id,
        operation="balance.get",
        status="SUCCESS",
        httpStatus=200,
    )

    return {
        "numeroCuenta": cuenta["numero_cuenta_enmascarado"],
        "saldo": cuenta["saldo"],
        "estado": cuenta["estado"],
    }


async def get_movements(user_id: str, trace_id: Optional[str] = None) -> Dict:
    movimientos_raw = await balance_repository.find_movements_by_user_id(user_id)

    movimientos_response = []
    for m in movimientos_raw:
        movimientos_response.append(
            {
                "movimientoId": str(m["id"]),
                "tipo": m["tipo"],
                "monto": m["monto"],
                "saldoAnterior": m["saldo_anterior"],
                "saldoPosterior": m["saldo_posterior"],
                "descripcion": m.get("descripcion"),
                "fecha": m["created_at"].isoformat() if m["created_at"] else None,
            }
        )

    log_event(
        "info",
        "Movimientos consultados exitosamente",
        traceId=trace_id,
        operation="movements.get",
        status="SUCCESS",
        httpStatus=200,
    )

    return {
        "movimientos": movimientos_response,
        "total": len(movimientos_response),
    }