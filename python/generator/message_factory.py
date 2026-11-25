from datetime import datetime, timezone
from typing import Any


def create_order_message(
    operation_id: str,
    order_id: str,
    run_id: str,
    attempt_id: str,
    amount: int,
    created_at: datetime,
) -> dict[str, Any]:
    """
    Формирует сообщение о создании заказа.

    Все идентификаторы должны быть непустыми строками.
    Сумма должна быть положительным целым числом.
    Дата должна содержать информацию о часовом поясе.
    """

    identifiers = {
        "operation_id": operation_id,
        "order_id": order_id,
        "run_id": run_id,
        "attempt_id": attempt_id,
    }

    for field, value in identifiers.items():
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{field} должен быть непустой строкой")

    if isinstance(amount, bool) or not isinstance(amount, int) or amount <= 0:
        raise ValueError("amount должен быть положительным целым числом")

    if not isinstance(created_at, datetime):
        raise TypeError("created_at должен иметь тип datetime")

    if created_at.tzinfo is None or created_at.utcoffset() is None:
        raise ValueError("created_at должен содержать часовой пояс")

    created_at_utc = created_at.astimezone(timezone.utc)

    return {
        "schema_version": 1,
        "operation_id": operation_id,
        "order_id": order_id,
        "amount": amount,
        "created_at": created_at_utc.isoformat(),
        "run_id": run_id,
        "attempt_id": attempt_id,
    }