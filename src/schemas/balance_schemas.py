# balance_schemas.py

from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class BalanceRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    user_id: str = Field(..., alias="userId")


class BalanceResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    numero_cuenta: str = Field(..., alias="numeroCuenta")
    saldo: Decimal
    estado: str


class MovementsRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    user_id: str = Field(..., alias="userId")


class MovementResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    movimiento_id: str = Field(..., alias="movimientoId")
    tipo: str  # DEBITO o CREDITO
    monto: Decimal
    saldo_anterior: Decimal = Field(..., alias="saldoAnterior")
    saldo_posterior: Decimal = Field(..., alias="saldoPosterior")
    descripcion: Optional[str] = None
    fecha: str = Field(..., alias="fecha")


class MovementsResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    movimientos: List[MovementResponse]
    total: int