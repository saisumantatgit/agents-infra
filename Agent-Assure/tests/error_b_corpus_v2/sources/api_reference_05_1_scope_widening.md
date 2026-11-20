# API reference: invoices

Responses include a `request_id` that support can look up. Use the `cursor` value from one page to request the next. The `cursor` parameter is optional.

The team responsible for the webhook queue received training during the review.

The status of the API is published on a public page. A sandbox environment mirrors the production API. Client libraries are available for several languages.

Version 9.1 of the API is the current release. The beta `cursor` filter never left preview and is not documented here. A `limit` above 21 is capped at 21.

Timestamps use the UTC time zone. Results are returned newest first. The invoices endpoint returns JSON. Every request must carry an API key in the `Authorization` header.

Webhooks are signed with a shared secret. All traffic uses encrypted connections. Field names use lower case letters and underscores.
