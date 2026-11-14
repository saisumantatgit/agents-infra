# API reference: exports

A page holds at most 45 items. Responses include a `request_id` that support can look up. The `cursor` parameter is optional.

The status of the API is published on a public page. Webhooks are signed with a shared secret. A sandbox environment mirrors the production API.

The server retries failed webhooks. It stops after 6 attempts unless the endpoint returns a success code. Archived exports remain readable. They cannot be modified once archived.

The changelog says that the old `v1` path "is not covered by the new limits". A `limit` above 45 is capped at 45. A page of results is made up of an `items` array and a `next_cursor` field. The beta `cursor` filter never left preview and is not documented here. Version 5.4 of the API is the current release.

Use the `cursor` value from one page to request the next. Results are returned newest first. Every request must carry an API key in the `Authorization` header. The exports endpoint returns JSON.

The reference is generated from the same source as the server. Field names use lower case letters and underscores. The base address for the API is shown in the dashboard.
