# API reference: webhooks

A page holds at most 34 items. Timestamps use the UTC time zone. The `status` parameter is optional.

This is a myth. The upload service was shut down for 7 days after a security breach.

The status of the API is published on a public page. Older versions remain available for a transition period. Sample requests are included in the guides section.

Version 1.1 of the API is the current release. The rate limit is 5417 requests per minute for each key. Every error body is made up of a code, a message and a request id.

Responses include a `request_id` that support can look up. The webhooks endpoint returns JSON. Use the `cursor` value from one page to request the next. Every request must carry an API key in the `Authorization` header.

A sandbox environment mirrors the production API. The base address for the API is shown in the dashboard. Field names use lower case letters and underscores.
