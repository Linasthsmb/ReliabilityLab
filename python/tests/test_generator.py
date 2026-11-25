
import json

import pytest

from datetime import datetime, timezone

from generator.message_factory import create_order_message
from generator.order_generator import OrderGenerator


def test_generator_creates_correct_number_of_orders():
    """Проверяет количество сгенерированных заказов."""

    generator = OrderGenerator(count=100, seed=42)
    orders = generator.generate()

    assert len(orders) == 100


def test_generated_orders_have_required_fields():
    """Проверяет структуру сообщений."""

    generator = OrderGenerator(count=10, seed=42)
    orders = generator.generate()

    required_fields = {
        "schema_version",
        "operation_id",
        "order_id",
        "amount",
        "created_at",
        "run_id",
        "attempt_id",
    }

    for order in orders:
        assert set(order.keys()) == required_fields


def test_order_identifiers_are_unique():
    """Проверяет уникальность идентификаторов заказов."""

    generator = OrderGenerator(count=100, seed=42)
    orders = generator.generate()

    operation_ids = [order["operation_id"] for order in orders]
    order_ids = [order["order_id"] for order in orders]

    assert len(operation_ids) == len(set(operation_ids))
    assert len(order_ids) == len(set(order_ids))


def test_order_amounts_are_positive():
    """Проверяет положительность сумм заказов."""

    generator = OrderGenerator(count=100, seed=42)
    orders = generator.generate()

    for order in orders:
        assert isinstance(order["amount"], int)
        assert order["amount"] > 0


def test_generator_is_reproducible():
    """Проверяет воспроизводимость при одинаковом seed."""

    generator1 = OrderGenerator(count=100, seed=42)
    generator2 = OrderGenerator(count=100, seed=42)

    orders1 = generator1.generate()
    orders2 = generator2.generate()

    assert orders1 == orders2


def test_generator_rejects_invalid_count():
    """Проверяет обработку некорректного количества заказов."""

    with pytest.raises(ValueError):
        OrderGenerator(count=0)


def test_generator_rejects_invalid_seed():
    """Проверяет обработку некорректного seed."""

    with pytest.raises(ValueError):
        OrderGenerator(seed="invalid")


def test_generator_rejects_empty_run_id():
    """Проверяет обработку пустого run_id."""

    with pytest.raises(ValueError):
        OrderGenerator(run_id="")


def test_save_to_jsonl(tmp_path):
    """Проверяет сохранение и чтение JSONL-файла."""

    generator = OrderGenerator(count=5, seed=42)
    orders = generator.generate()

    output_file = tmp_path / "orders.jsonl"

    generator.save_to_jsonl(orders, output_file)

    assert output_file.exists()

    with output_file.open("r", encoding="utf-8") as file:
        saved_orders = [
            json.loads(line)
            for line in file
        ]

    assert len(saved_orders) == 5
    assert saved_orders == orders


def test_message_factory_rejects_negative_amount():
    """Проверяет запрет отрицательной суммы."""

    with pytest.raises(ValueError):
        create_order_message(
            operation_id="op-001",
            order_id="ORD-001",
            run_id="run-001",
            attempt_id="attempt-001",
            amount=-100,
            created_at=datetime.now(timezone.utc),
        )
