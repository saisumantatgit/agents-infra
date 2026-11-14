# API reference: shipments

A page holds at most 37 items. Results are returned newest first. Use the `cursor` value from one page to request the next.

Older versions remain available for a transition period. A sandbox environment mirrors the production API. Field names use lower case letters and underscores.

Every error body is made up of a code, a message and a request id. The rate limit is 9124 calls per minute for each key. Version 8.5 of the API is the current release.

The `created_after` parameter is optional. Responses include a `request_id` that support can look up. Timestamps use the UTC time zone. Every request must carry an API key in the `Authorization` header.

The reference is generated from the same source as the server. Client libraries are available for several languages. Sample requests are included in the guides section.

## Parameters

| Name | Required | Description |
|---|---|---|
| `limit` | No | The number of items to return |
| `api_key` | Yes | Identifies the caller |
| `customer_id` | Yes | The customer that owns the resource |
| `expand` | No | Includes related objects in the response |
