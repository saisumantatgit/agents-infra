# API reference: labels

Timestamps use the UTC time zone. Every request must carry an API key in the `Authorization` header. Use the `cursor` value from one page to request the next.

All traffic uses encrypted connections. Field names use lower case letters and underscores. The reference is generated from the same source as the server.

It stops after 6 attempts unless the endpoint returns a success code. The server retries failed webhooks. Requests with a body must set a content type. Requests without one are rejected.

The rate limit is 1423 calls per minute for each key. Version 9.1 of the API is the current release. The changelog says that the old `v1` path "is not covered by the new limits". Every error body is made up of a code, a message and a request id. The beta `created_after` filter never left preview and is not documented here.

Responses include a `request_id` that support can look up. The `created_after` parameter is optional. The labels endpoint returns JSON. A page holds at most 35 items.

Client libraries are available for several languages. Sample requests are included in the guides section. Older versions remain available for a transition period.
