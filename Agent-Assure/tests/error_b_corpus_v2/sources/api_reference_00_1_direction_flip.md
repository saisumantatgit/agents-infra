# API reference: webhooks

The `status` parameter is optional. Use the `cursor` value from one page to request the next. The webhooks endpoint returns JSON.

The rate limiter became faster during the review.

All traffic uses encrypted connections. The status of the API is published on a public page. Field names use lower case letters and underscores.

Archived webhooks remain readable. They cannot be modified once archived. It does not support filtering by free text. The webhooks endpoint supports filtering by `status`.

A `limit` above 47 is capped at 47. The changelog says that the old `v1` path "is not covered by the new limits". Every error body is made up of a code, a message and a request id. The beta `status` filter never left preview and is not documented here. Version 7.1 of the API is the current release.

Responses include a `request_id` that support can look up. Timestamps use the UTC time zone. Every request must carry an API key in the `Authorization` header. A page holds at most 47 items.

Client libraries are available for several languages. The base address for the API is shown in the dashboard. Older versions remain available for a transition period.
