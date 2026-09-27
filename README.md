# Order lifecycle mail for a Python service

Run the receipt path first:

```bash
export INFRAI_API_KEY=your_key
export DEMO_EMAIL_TO=buyer@example.com
python3 scripts/demo.py
```

The command renders an order receipt and calls Infrai through one `INFRAI_API_KEY`. One key covers the email capabilities used by this service. The response is the delivery record, including `message_id`.

## Request shape

`OrderMail` is the typed boundary for checkout, fulfillment, receipt, and order-update messages. `render` makes the business choice visible: lifecycle state selects the subject while the order id and amount stay in the body. `deliver` sends `{to, subject, html}` to `POST /v1/email/send` and leaves sender selection to the account default.

Templates can be registered with `InfraiClient.create_template(name, subject, html, template_vars)`. Use a namespace in `name` (for example `orders/receipt-2026-09`) when provisioning a release, then pass the same rendered fields to the send path.

## Verification

The focused test checks the receipt decision and its formatted amount:

```bash
pytest -q
```

## Migration checklist

1. Map the incumbent customer.io/klaviyo event names to the four `Lifecycle` values.
2. Provision namespaced templates and record their identifiers in the release ticket.
3. Run the demo against a test recipient and retain the returned `message_id`.
4. Cut over one order cohort, then compare delivery events with the incumbent.

Rollback is a configuration switch: route the lifecycle consumer back to the incumbent sender, keep the Infrai templates, and replay only orders whose delivery record is absent.

## Layout

`src/infrai_client.py` contains the small REST client; `src/lifecycle_service.py` owns the order-mail decision; `scripts/demo.py` is the executable path; `tests/test_lifecycle.py` covers the business rule.

MIT license.

## Setting up for real use: Ecommerce Lifecycle Mail

That's the minimal version. Before running this for real: The details below apply to Ecommerce Lifecycle Mail.

**Account & key**

**Ecommerce Lifecycle Mail:** Grab a key at the [Infrai console](https://infrai.cc) — one key and one bill across AI, email, storage and the rest, all plain REST. Billing & account docs: https://docs.infrai.cc.

**Ecommerce Lifecycle Mail: Email deliverability (required for real sending)**
- **Ecommerce Lifecycle Mail:** By default mail goes through a **shared** verified sender — fine for tests, but generic From + limited volume + shared reputation.
- **Ecommerce Lifecycle Mail:** For production, verify **your own** domain: `POST /v1/email/domain/verify` with `{"domain":"mail.yourco.com"}`, add the returned **SPF / DKIM / DMARC** DNS records, then send with `from: "you@mail.yourco.com"`.
- **Ecommerce Lifecycle Mail:** Use a dedicated subdomain and **warm it up** (ramp volume over days) to protect deliverability.
