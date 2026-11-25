
import json

import httpx
import pytest

from datetime import datetime, timezone

from adapter.message_validator import validate_order_message
from adapter.response_handler import (
    handle_response,
    OperationStatus,
)
from adapter.event_logger import EventLogger
from adapter.element_client import ElementClient


# --------------------------------------------------
# Вспомогательная функция
# --------------------------------------------------

def create_valid_message():
    """Создаёт корректное тестовое сообщение."""

    return {
        "schema_version": 1,
        "operation_id": "op-000001",
        "order_id": "ORD-000001",
        "amount": 1500,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "run_id": "run-001",
        "attempt_id": "attempt-000001-001",
    }


# --------------------------------------------------
# Тесты MessageValidator
# --------------------------------------------------

def test_validator_accepts_valid_message():
    """Проверяет принятие корректного сообщения."""

    message = create_valid_message()

    validate_order_message(message)


def test_validator_rejects_non_dict():
    """Проверяет отклонение сообщения неправильного типа."""

    with pytest.raises(ValueError):
        validate_order_message("invalid")


def test_validator_rejects_missing_fields():
    """Проверяет отсутствие обязательных полей."""

    message = create_valid_message()
    del message["order_id"]

    with pytest.raises(ValueError):
        validate_order_message(message)


def test_validator_rejects_unsupported_schema_version():
    """Проверяет неподдерживаемую версию схемы."""

    message = create_valid_message()
    message["schema_version"] = 2

    with pytest.raises(ValueError):
        validate_order_message(message)


def test_validator_rejects_invalid_amount():
    """Проверяет отклонение некорректной суммы."""

    message = create_valid_message()
    message["amount"] = -100

    with pytest.raises(ValueError):
        validate_order_message(message)


def test_validator_rejects_boolean_amount():
    """Проверяет, что bool не принимается как сумма."""

    message = create_valid_message()
    message["amount"] = True

    with pytest.raises(ValueError):
        validate_order_message(message)


def test_validator_rejects_invalid_date():
    """Проверяет некорректный формат даты."""

    message = create_valid_message()
    message["created_at"] = "invalid-date"

    with pytest.raises(ValueError):
        validate_order_message(message)


def test_validator_rejects_date_without_timezone():
    """Проверяет обязательность часового пояса."""

    message = create_valid_message()
    message["created_at"] = "2026-11-20T12:00:00"

    with pytest.raises(ValueError):
        validate_order_message(message)


# --------------------------------------------------
# Тесты ResponseHandler
# --------------------------------------------------

@pytest.mark.parametrize(
    "status_code, expected",
    [
        (200, OperationStatus.SUCCESS),
        (201, OperationStatus.SUCCESS),
        (204, OperationStatus.SUCCESS),
        (400, OperationStatus.FAILURE),
        (404, OperationStatus.FAILURE),
        (500, OperationStatus.UNKNOWN),
        (503, OperationStatus.UNKNOWN),
        (302, OperationStatus.UNKNOWN),
    ],
)
def test_response_handler_status_codes(status_code, expected):
    """Проверяет классификацию HTTP-ответов."""

    result = handle_response(status_code)

    assert result == expected


def test_response_handler_timeout():
    """Проверяет неопределённый результат при тайм-ауте."""

    result = handle_response(
        None,
        error=TimeoutError(),
    )

    assert result == OperationStatus.UNKNOWN


def test_response_handler_without_response():
    """Проверяет результат при отсутствии HTTP-ответа."""

    result = handle_response(None)

    assert result == OperationStatus.UNKNOWN


# --------------------------------------------------
# Тесты EventLogger
# --------------------------------------------------

def test_event_logger_creates_file(tmp_path):
    """Проверяет создание файла журнала."""

    output_file = tmp_path / "events.jsonl"

    logger = EventLogger(output_file)

    logger.log_event(
        operation_id="op-000001",
        event="request_sent",
        status="unknown",
        details={"reason": "timeout"},
    )

    assert output_file.exists()


def test_event_logger_saves_correct_data(tmp_path):
    """Проверяет корректность записанного события."""

    output_file = tmp_path / "events.jsonl"

    logger = EventLogger(output_file)

    logger.log_event(
        operation_id="op-000001",
        event="request_sent",
        status="unknown",
        details={"reason": "timeout"},
    )

    with output_file.open("r", encoding="utf-8") as file:
        event = json.loads(file.readline())

    assert event["operation_id"] == "op-000001"
    assert event["event"] == "request_sent"
    assert event["status"] == "unknown"
    assert event["details"]["reason"] == "timeout"

    # Проверяем корректность временной метки.
    datetime.fromisoformat(event["timestamp"])


def test_event_logger_appends_events(tmp_path):
    """Проверяет добавление нескольких событий."""

    output_file = tmp_path / "events.jsonl"

    logger = EventLogger(output_file)

    logger.log_event("op-001", "request_sent", "unknown")
    logger.log_event("op-001", "response_received", "success")

    with output_file.open("r", encoding="utf-8") as file:
        events = [json.loads(line) for line in file]

    assert len(events) == 2


# --------------------------------------------------
# Тесты ElementClient
# --------------------------------------------------

def test_element_client_sends_post_request():
    """Проверяет отправку POST-запроса."""

    order_data = create_valid_message()

    def mock_handler(request):
        assert request.method == "POST"
        assert request.url.path == "/api/orders"

        received_data = json.loads(request.content)

        assert received_data == order_data

        return httpx.Response(
            201,
            json={"result": "created"},
        )

    transport = httpx.MockTransport(mock_handler)

    client = ElementClient(
        base_url="https://example.test",
        transport=transport,
    )

    response = client.create_order(
        endpoint="/api/orders",
        order_data=order_data,
    )

    assert response.status_code == 201
    assert response.json()["result"] == "created"


def test_element_client_propagates_timeout():
    """Проверяет передачу ошибки тайм-аута вызывающему коду."""

    def mock_handler(request):
        raise httpx.ReadTimeout(
            "Request timed out",
            request=request,
        )

    transport = httpx.MockTransport(mock_handler)

    client = ElementClient(
        base_url="https://example.test",
        transport=transport,
    )

    with pytest.raises(httpx.ReadTimeout):
        client.create_order(
            endpoint="/api/orders",
            order_data=create_valid_message(),
        )


def test_element_client_rejects_empty_url():
    """Проверяет запрет пустого базового URL."""

    with pytest.raises(ValueError):
        ElementClient(base_url="")
