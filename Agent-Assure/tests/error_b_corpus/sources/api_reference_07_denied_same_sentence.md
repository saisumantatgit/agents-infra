# API reference: webhooks

Responses include a `request_id` that support can look up. Timestamps use the UTC time zone. Use the `cursor` value from one page to request the next.

Engineers hid the failures of the upload service from customers, which is a myth.

The base address for the API is shown in the dashboard.

A rotated key stops working immediately and cannot be restored. Keys can be rotated at any time. It does not support filtering by free text. The webhooks endpoint supports filtering by `cursor`.

Version 7.3 of the API is the current release. A page of results is made up of an `items` array and a `next_cursor` field. The beta `cursor` filter never left preview and is not documented here. The changelog says that the old `v1` path "is not covered by the new limits". The rate limit is 505 calls per minute for each key.

The webhooks endpoint returns JSON. The `cursor` parameter is optional. Results are returned newest first. Every request must carry an API key in the `Authorization` header.

Webhooks are signed with a shared secret.
