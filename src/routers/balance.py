from fastapi import APIRouter, Depends, HTTPException, Request

from src.middlewares.session_middleware import require_session
from src.schemas.balance_schemas import (
    BalanceRequest,
    BalanceResponse,
    MovementsRequest,
    MovementsResponse,
)
from src.services import balance_service
from src.utils.logger import log_event


router = APIRouter()


def _validate_user_match(
    session: dict,
    body_user_id: str,
    trace_id: str,
    operation: str,
) -> None:
    session_user_id = str(session.get("userId") or session.get("user_id") or "")
    if not session_user_id or session_user_id != str(body_user_id):
        log_event(
            "warning",
            "User_id no coincide con la sesión",
            traceId=trace_id,
            operation=operation,
            status="ERROR",
            httpStatus=403,
            errorCode="USER_MISMATCH",
        )
        raise HTTPException(
            status_code=403,
            detail={
                "errorCode": "USER_MISMATCH",
                "message": "El usuario no coincide con la sesión",
            },
        )


@router.post(
    "/balance",
    response_model=BalanceResponse,
    response_model_by_alias=True,
)
async def get_balance(
    payload: BalanceRequest,
    request: Request,
    session: dict = Depends(require_session),
):
    trace_id = request.state.trace_id
    _validate_user_match(session, payload.user_id, trace_id, "balance.get")

    result = await balance_service.get_balance(payload.user_id, trace_id)
    return result


@router.post(
    "/movements",
    response_model=MovementsResponse,
    response_model_by_alias=True,
)
async def get_movements(
    payload: MovementsRequest,
    request: Request,
    session: dict = Depends(require_session),
):
    trace_id = request.state.trace_id
    _validate_user_match(session, payload.user_id, trace_id, "movements.get")

    result = await balance_service.get_movements(payload.user_id, trace_id)
    return result