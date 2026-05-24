from typing import Dict, List, Optional

import asyncpg

from src.config.database import get_db_pool


def _mask_account(numero_cuenta: str) -> str:
    if len(numero_cuenta) <= 4:
        return numero_cuenta
    return "****" + numero_cuenta[-4:]


async def find_balance_by_user_id(user_id: str) -> Optional[Dict]:
    pool = get_db_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            SELECT id, numero_cuenta, saldo, estado
            FROM cuentas
            WHERE usuario_id = $1
            """,
            user_id,
        )
        if not row:
            return None

        account = dict(row)
        account["numero_cuenta_enmascarado"] = _mask_account(account["numero_cuenta"])
        return account


async def find_movements_by_user_id(user_id: str, limit: int = 50) -> List[Dict]:
    pool = get_db_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT m.id, m.tipo, m.monto, m.saldo_anterior,
                   m.saldo_posterior, m.descripcion, m.created_at
            FROM movimientos m
            JOIN cuentas c ON m.cuenta_id = c.id
            WHERE c.usuario_id = $1
            ORDER BY m.created_at DESC
            LIMIT $2
            """,
            user_id,
            limit,
        )
        return [dict(row) for row in rows]