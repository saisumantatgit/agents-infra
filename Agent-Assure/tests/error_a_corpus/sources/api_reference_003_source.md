# API reference: labels

The labels endpoint returns JSON. The `cursor` parameter is optional. A page holds at most 35 items.

A sandbox environment mirrors the production API.

Requests without one are rejected. Requests with a body must set a content type. A rotated key stops working immediately and cannot be restored. Keys can be rotated at any time.

The changelog says that the old `v1` path "is not covered by the new limits". Every error body is made up of a code, a message and a request id. The beta `cursor` filter never left preview and is not documented here. A `limit` above 35 is capped at 35. Version 9.7 of the API is the current release.

Responses include a `request_id` that support can look up. Every request must carry an API key in the `Authorization` header. Results are returned newest first. Use the `cursor` value from one page to request the next.

The base address for the API is shown in the dashboard.
