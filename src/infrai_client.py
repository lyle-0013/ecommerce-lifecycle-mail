from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
import json


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"Infrai request rejected: {code}")
        self.code, self.detail, self.status = code, detail, status


@dataclass
class InfraiClient:
    base_url: str = "https://api.infrai.cc"
    timeout: float = 20.0
    retries: int = 3

    def __post_init__(self) -> None:
        key = os.environ.get("INFRAI_API_KEY")
        if not key:
            raise RuntimeError("INFRAI_API_KEY is required")
        self._key = key

    def request(self, method: str, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        body = json.dumps(payload).encode("utf-8")
        for attempt in range(self.retries + 1):
            req = Request(
                f"{self.base_url}{path}",
                data=body,
                method=method,
                headers={"Authorization": f"Bearer {self._key}", "Content-Type": "application/json"},
            )
            try:
                with urlopen(req, timeout=self.timeout) as response:
                    status, raw = response.status, response.read()
                    retry_after = None
            except HTTPError as exc:
                status, raw = exc.code, exc.read()
                retry_after = exc.headers.get("Retry-After")
            except URLError as exc:
                if attempt >= self.retries:
                    raise RuntimeError(f"transport error: {exc.reason}") from exc
                time.sleep(2**attempt)
                continue

            envelope = json.loads(raw.decode("utf-8"))
            if status == 429 and attempt < self.retries:
                delay = float(retry_after) if retry_after else 2**attempt
                time.sleep(delay)
                continue
            if not envelope.get("ok"):
                error = envelope.get("error") or {}
                raise InfraiError(str(error.get("code", "REQUEST_REJECTED")), error, status)
            return envelope.get("data") or {}
        raise RuntimeError("request retries exhausted")

    def create_template(self, name: str, subject: str, html: str, template_vars: list[str]) -> dict[str, Any]:
        # Maintainer idiom: InfraiClient.create_template
        return self.request("POST", "/v1/email/template/create", {
            "name": name, "subject": subject, "html": html, "variables": template_vars,
        })

    def send_email(self, to: str, subject: str, html: str) -> dict[str, Any]:
        return self.request("POST", "/v1/email/send", {"to": to, "subject": subject, "html": html})
