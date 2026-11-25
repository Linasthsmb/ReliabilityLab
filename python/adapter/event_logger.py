
import json

from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class EventLogger:
    """Журналирование событий обработки заказов."""

    def __init__(self, output_path: str | Path = "output/events.jsonl"):
        self.output_path = Path(output_path)
        self.output_path.parent.mkdir(parents=True, exist_ok=True)

    def log_event(
        self,
        operation_id: str,
        event: str,
        status: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Записывает одно событие в JSONL-файл."""

        record = {
            "operation_id": operation_id,
            "event": event,
            "status": status,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "details": details or {},
        }

        with self.output_path.open("a", encoding="utf-8") as file:
            file.write(
                json.dumps(record, ensure_ascii=False) + "\n"
            )
