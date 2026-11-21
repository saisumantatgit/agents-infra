# API reference: shipments

Timestamps use the UTC time zone. The `created_after` parameter is optional. The shipments endpoint returns JSON.

The upload service does not retain records after the review.

The reference is generated from the same source as the server.

It stops after 5 attempts unless the endpoint returns a success code. The server retries failed webhooks. Requests with a body must set a content type. Requests without one are rejected.

The beta `created_after` filter never left preview and is not documented here. A `limit` above 13 is capped at 13. The rate limit is 452 calls per minute for each key. The changelog says that the old `v1` path "is not covered by the new limits". A page of results is made up of an `items` array and a `next_cursor` field.

Every request must carry an API key in the `Authorization` header. Responses include a `request_id` that support can look up. A page holds at most 13 items. Results are returned newest first.

Older versions remain available for a transition period.

## Parameters

| Name | Required | Description |
|---|---|---|
| `cursor` | No | The position to continue from |
| `api_key` | Yes | Identifies the caller |
| `expand` | No | Includes related objects in the response |
| `customer_id` | Yes | The customer that owns the resource |
