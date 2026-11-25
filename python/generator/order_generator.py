
import json
import random

from datetime import datetime, timedelta, timezone
from pathlib import Path

from generator.message_factory import create_order_message


class OrderGenerator:
    """
    Генератор тестовых сообщений о заказах.

    Позволяет создавать воспроизводимые наборы данных
    с использованием фиксированного seed.
    """

    def __init__(
        self,
        count: int = 100,
        seed: int = 42,
        run_id: str = "run-001",
    ):
        if count <= 0:
            raise ValueError("Количество заказов должно быть больше нуля")

        if not isinstance(seed, int) or isinstance(seed, bool):
            raise ValueError("seed должен быть целым числом")

        if not isinstance(run_id, str) or not run_id.strip():
            raise ValueError("run_id должен быть непустой строкой")

        self.count = count
        self.seed = seed
        self.run_id = run_id

        # Отдельный генератор случайных чисел для воспроизводимости.
        self.random = random.Random(seed)

        # Фиксированная дата начала генерации в UTC.
        self.base_time = datetime(
            2026, 11, 20, 0, 0, 0,
            tzinfo=timezone.utc,
        )

    def generate(self) -> list[dict]:
        """Создаёт набор сообщений о заказах."""

        orders = []

        for i in range(1, self.count + 1):
            operation_id = f"op-{i:06d}"
            order_id = f"ORD-{i:06d}"
            attempt_id = f"attempt-{i:06d}-001"

            amount = self.random.randint(100, 100000)

            created_at = self.base_time + timedelta(seconds=i)

            message = create_order_message(
                operation_id=operation_id,
                order_id=order_id,
                run_id=self.run_id,
                attempt_id=attempt_id,
                amount=amount,
                created_at=created_at,
            )

            orders.append(message)

        return orders

    def save_to_jsonl(
        self,
        orders: list[dict],
        output_path: str | Path,
    ) -> None:
        """Сохраняет сообщения в формате JSONL."""

        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with path.open("w", encoding="utf-8") as file:
            for order in orders:
                file.write(
                    json.dumps(order, ensure_ascii=False) + "\n"
                )

        print(f"Сохранено заказов: {len(orders)}")
        print(f"Файл: {path.resolve()}")


if __name__ == "__main__":
    generator = OrderGenerator(
        count=100,
        seed=42,
        run_id="run-001",
    )

    orders = generator.generate()

    generator.save_to_jsonl(
        orders,
        "output/orders.jsonl",
    )
