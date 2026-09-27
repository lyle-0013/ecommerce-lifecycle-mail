import os
from decimal import Decimal
from src.infrai_client import InfraiClient
from src.lifecycle_service import OrderMail, deliver


def main() -> None:
    recipient = os.environ.get("DEMO_EMAIL_TO")
    if not recipient:
        raise SystemExit("DEMO_EMAIL_TO is required")
    mail = OrderMail("receipt", recipient, "ORD-1042", "Ari", Decimal("49.90"))
    result = deliver(mail, InfraiClient())
    print(f"sent receipt message_id={result.get('message_id')}")


if __name__ == "__main__":
    main()
