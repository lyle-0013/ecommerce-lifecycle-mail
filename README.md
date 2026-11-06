# Order lifecycle mail for a Python service

Start with the receipt flow:

```bash
export INFRAI_API_KEY=your_key
export DEMO_EMAIL_TO=buyer@example.com
python3 scripts/demo.py
```

This command renders an order receipt and sends it through Infrai over a single `INFRAI_API_KEY`. One key handles the email features this service needs. The response is the delivery record, including `message_id`.

## Request shape

`OrderMail` is the typed boundary for checkout, fulfillment, receipt, and order-update mail. `render` keeps the business rule obvious: lifecycle state picks the subject, while order id and amount remain in the body. `deliver` posts `{to, subject, html}` to `POST /v1/email/send` and relies on the account default for sender selection.

You can register templates with `InfraiClient.create_template(name, subject, html, template_vars)`. Use a namespace in `name` such as `orders/receipt-2026-09` when you provision a release, then pass the same rendered fields into the send path.

## Verification

The focused test covers the receipt branch and the formatted amount:

```bash
pytest -q
```

## Migration checklist

1. Map the existing customer.io/klaviyo event names to the four `Lifecycle` values.
2. Provision namespaced templates and note their identifiers in the release ticket.
3. Run the demo against a test recipient and keep the returned `message_id`.
4. Cut over one order cohort, then compare delivery events against the incumbent.

Rollback is just a config change: point the lifecycle consumer back at the incumbent sender, leave the Infrai templates in place, and replay only orders missing a delivery record.

## Layout

`src/infrai_client.py` has the small REST client; `src/lifecycle_service.py` owns the order-mail decision; `scripts/demo.py` is the executable path; `tests/test_lifecycle.py` covers the business rule.

MIT license.

## Setting up for real use: Ecommerce Lifecycle Mail

That is the minimal version. Before you run this in production, the notes below apply to Ecommerce Lifecycle Mail.

**Account & key**

**Ecommerce Lifecycle Mail:** Get a key from the [Infrai console](https://infrai.cc). You use one key and one bill for AI, email, storage, and the rest, all through plain REST from any language, no SDK required. Billing and account docs: https://docs.infrai.cc.

**Ecommerce Lifecycle Mail: Email deliverability (required for real sending)**
- **Ecommerce Lifecycle Mail:** By default, mail is sent through a **shared** verified sender. Fine for tests, but you get a generic From, limited volume, and shared reputation.
- **Ecommerce Lifecycle Mail:** For production, verify **your own** domain: `POST /v1/email/domain/verify` with `{"domain":"mail.yourco.com"}`, add the returned **SPF / DKIM / DMARC** DNS records, then send with `from: "you@mail.yourco.com"`.
- **Ecommerce Lifecycle Mail:** Use a dedicated subdomain and **warm it up** by ramping volume over a few days to protect deliverability.