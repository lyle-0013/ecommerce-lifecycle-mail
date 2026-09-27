from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Literal
from .infrai_client import InfraiClient


Lifecycle = Literal["checkout", "fulfillment", "receipt", "order_update"]


@dataclass(frozen=True)
class OrderMail:
    lifecycle: Lifecycle
    recipient: str
    order_id: str
    customer_name: str
    total: Decimal


def render(mail: OrderMail) -> tuple[str, str]:
    labels = {
        "checkout": "Checkout received",
        "fulfillment": "Order shipped",
        "receipt": "Your receipt",
        "order_update": "Order update",
    }
    subject = f"{labels[mail.lifecycle]}: {mail.order_id}"
    html = f"<p>Hello {mail.customer_name},</p><p>Order <b>{mail.order_id}</b> totals ${mail.total:.2f}.</p>"
    return subject, html


def deliver(mail: OrderMail, client: InfraiClient) -> dict[str, object]:
    subject, html = render(mail)
    return client.send_email(mail.recipient, subject, html)
