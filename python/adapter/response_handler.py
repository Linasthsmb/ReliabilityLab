
from enum import Enum
from typing import Any


class OperationStatus(Enum):
    """Возможные результаты выполнения операции."""

    SUCCESS = "success"
    FAILURE = "failure"
    UNKNOWN = "unknown"


def handle_response(
    status_code: int | None,
    response_body: dict[str, Any] | None = None,
    error: Exception | None = None,
) -> OperationStatus:
    """
    Определяет результат HTTP-взаимодействия с Element.

    status_code:
        HTTP-код ответа или None, если ответ не получен.

    response_body:
        Тело HTTP-ответа.

    error:
        Ошибка при выполнении запроса.
    """

    # Ответ не получен: результат операции неизвестен.
    if error is not None or status_code is None:
        return OperationStatus.UNKNOWN

    # Успешный HTTP-ответ.
    if 200 <= status_code < 300:
        return OperationStatus.SUCCESS

    # Получен однозначный отказ.
    if 400 <= status_code < 500:
        return OperationStatus.FAILURE

    # Серверная ошибка может возникнуть уже после выполнения операции.
    if 500 <= status_code < 600:
        return OperationStatus.UNKNOWN

    # Неожиданные HTTP-коды.
    return OperationStatus.UNKNOWN
