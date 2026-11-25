
from datetime import datetime
from typing import Any


# Обязательные поля сообщения, которое формирует OrderGenerator.
REQUIRED_FIELDS = {
    "schema_version",
    "operation_id",
    "order_id",
    "amount",
    "created_at",
    "run_id",
    "attempt_id",
}


def validate_order_message(message: dict[str, Any]) -> None:
    """
    Проверяет входящее сообщение о создании заказа.

    При корректном сообщении ничего не возвращает.
    При обнаружении ошибки выбрасывает ValueError.
    """

    # Проверяем тип входных данных.
    if not isinstance(message, dict):
        raise ValueError("Сообщение должно быть словарём")

    # Проверяем наличие обязательных полей.
    missing_fields = REQUIRED_FIELDS - message.keys()

    if missing_fields:
        raise ValueError(
            f"Отсутствуют обязательные поля: {sorted(missing_fields)}"
        )

    # Проверяем версию схемы.
    if type(message["schema_version"]) is not int:
        raise ValueError("schema_version должен быть целым числом")

    if message["schema_version"] != 1:
        raise ValueError("Неподдерживаемая версия схемы сообщения")

    # Проверяем идентификаторы.
    identifier_fields = [
        "operation_id",
        "order_id",
        "run_id",
        "attempt_id",
    ]

    for field in identifier_fields:
        value = message[field]

        if not isinstance(value, str) or not value.strip():
            raise ValueError(
                f"{field} должен быть непустой строкой"
            )

    # Проверяем сумму заказа.
    amount = message["amount"]

    if type(amount) is not int or amount <= 0:
        raise ValueError(
            "amount должен быть положительным целым числом"
        )

    # Проверяем дату создания заказа.
    created_at = message["created_at"]

    if not isinstance(created_at, str):
        raise ValueError("created_at должен быть строкой")

    try:
        parsed_date = datetime.fromisoformat(
            created_at.replace("Z", "+00:00")
        )
    except ValueError:
        raise ValueError(
            "created_at должен содержать корректную дату ISO 8601"
        )

    # Дата обязательно должна содержать часовой пояс.
    if (
        parsed_date.tzinfo is None
        or parsed_date.utcoffset() is None
    ):
        raise ValueError(
            "created_at должен содержать часовой пояс"
        )
