
from typing import Any

import httpx


class ElementClient:
    """HTTP-клиент для взаимодействия с API Element."""

    def __init__(
        self,
        base_url: str,
        timeout: float = 10.0,
        transport: httpx.BaseTransport | None = None,
    ):
        if not isinstance(base_url, str) or not base_url.strip():
            raise ValueError("base_url не должен быть пустым")

        if timeout <= 0:
            raise ValueError("timeout должен быть больше нуля")

        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.transport = transport

    def create_order(
        self,
        endpoint: str,
        order_data: dict[str, Any],
    ) -> httpx.Response:
        """Отправляет POST-запрос на создание заказа."""

        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        with httpx.Client(
            timeout=self.timeout,
            transport=self.transport,
        ) as client:
            response = client.post(
                url,
                json=order_data,
            )

        return response
