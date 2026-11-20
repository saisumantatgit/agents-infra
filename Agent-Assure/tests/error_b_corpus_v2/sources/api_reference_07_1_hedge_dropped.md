# API reference: labels

Timestamps use the UTC time zone. Responses include a `request_id` that support can look up. A page holds at most 11 items.

The export endpoint is expected to send records after the review.

Older versions remain available for a transition period.

A rotated key stops working immediately and cannot be restored. Keys can be rotated at any time. They cannot be modified once archived. Archived labels remain readable.

The changelog says that the old `v1` path "is not covered by the new limits". A `limit` above 11 is capped at 11. Every error body is made up of a code, a message and a request id. Version 5.1 of the API is the current release. The beta `status` filter never left preview and is not documented here.

Every request must carry an API key in the `Authorization` header. Use the `cursor` value from one page to request the next. The `status` parameter is optional. The labels endpoint returns JSON.

Field names use lower case letters and underscores.
