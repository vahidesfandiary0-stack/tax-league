# Manual bank-transfer payment workflow

## Customer flow
1. Authenticated customer lists active subscription plans at `GET /api/v1/payments/plans/`.
2. Customer requests an order at `POST /api/v1/payments/orders/create/` with either `product_type=subscription, plan_id` or `product_type=exam, exam_id`. Price is read from the server-side product, never accepted from the client.
3. Customer reads bank-transfer details from authenticated `GET /api/v1/payments/instructions/`.
4. Customer uploads a JPG, PNG, or PDF receipt (max 5 MiB) to `POST /api/v1/payments/orders/<uuid>/submit/` as multipart form data. Optional fields: `tracking_code`, `note`.
5. Staff reviews the order in Django admin. Approval grants a subscription or purchased-exam entitlement transactionally; rejection does not grant access.

## APIs
- `GET /api/v1/payments/plans/`
- `GET /api/v1/payments/instructions/` (authenticated; card number is never in public endpoints or order serializers)
- `GET /api/v1/payments/orders/`
- `POST /api/v1/payments/orders/create/`
- `GET /api/v1/payments/orders/<uuid>/` (owner only)
- `POST /api/v1/payments/orders/<uuid>/submit/` (owner only)
- `GET /api/v1/payments/staff/orders/<uuid>/receipt/` (staff only)

## Admin and security
- Configure the single payment card record under Payment settings. Only superusers can view or edit it.
- Payment approval/rejection uses admin actions and a database transaction. Admin users cannot manually edit order status.
- Order product and amount are immutable snapshots. A one-to-one source-order constraint prevents duplicate entitlement creation from repeated approval.
- Receipts are not included in customer API responses. Download is via a staff-only endpoint.
- Production Nginx/storage MUST NOT expose `MEDIA_ROOT` or the private receipt directory as a public static/media URL. Use private object storage or a non-public disk, TLS, backups, malware scanning, and audited staff access. The local FileField storage in this scaffold is not by itself a hardened private-storage implementation.
- Card number is stored in the database and protected by superuser-only admin/API authentication; production should encrypt sensitive configuration at rest and audit changes.

## Known limitations before launch
- Add malware scanning and stronger image/PDF parser validation.
- Add an audited admin review history table and notifications.
- Define refund/cancellation handling and subscription revocation.
- Run migrations and tests on PostgreSQL; verify concurrency, file privacy, and authorization.
