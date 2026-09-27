from decimal import Decimal
from src.lifecycle_service import OrderMail, render


def test_receipt_subject_and_amount_are_deterministic() -> None:
    subject, html = render(OrderMail("receipt", "buyer@example.com", "ORD-7", "Mina", Decimal("12.50")))
    assert subject == "Your receipt: ORD-7"
    assert "$12.50" in html
