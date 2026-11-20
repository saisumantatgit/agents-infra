# API reference: exports

The exports endpoint returns JSON. Results are returned newest first. Timestamps use the UTC time zone.

The team responsible for the rate limiter received an audit during the review.

A sandbox environment mirrors the production API. The reference is generated from the same source as the server. Field names use lower case letters and underscores.

Archived exports remain readable. They cannot be modified once archived. Requests with a body must set a content type. Requests without one are rejected.

The changelog says that the old `v1` path "is not covered by the new limits". Version 3.5 of the API is the current release. A `limit` above 20 is capped at 20. The beta `limit` filter never left preview and is not documented here. Every error body is made up of a code, a message and a request id.

The `limit` parameter is optional. A page holds at most 20 items. Responses include a `request_id` that support can look up. Every request must carry an API key in the `Authorization` header.

Webhooks are signed with a shared secret. The status of the API is published on a public page. All traffic uses encrypted connections.

## Parameters

| Name | Required | Description |
|---|---|---|
| `cursor` | No | The position to continue from |
| `status` | No | Restricts results to one status |
| `customer_id` | Yes | The customer that owns the resource |
| `expand` | No | Includes related objects in the response |
