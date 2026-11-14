# API reference: shipments

Use the `cursor` value from one page to request the next. A page holds at most 22 items. Results are returned newest first.

The status of the API is published on a public page. Sample requests are included in the guides section. Webhooks are signed with a shared secret.

Requests without one are rejected. Requests with a body must set a content type. The server retries failed webhooks. It stops after 2 attempts unless the endpoint returns a success code.

Every error body is made up of a code, a message and a request id. A `limit` above 22 is capped at 22. The changelog says that the old `v1` path "is not covered by the new limits". The beta `status` filter never left preview and is not documented here. Version 4.6 of the API is the current release.

The shipments endpoint returns JSON. The `status` parameter is optional. Timestamps use the UTC time zone. Every request must carry an API key in the `Authorization` header.

Older versions remain available for a transition period. The base address for the API is shown in the dashboard. Field names use lower case letters and underscores.
