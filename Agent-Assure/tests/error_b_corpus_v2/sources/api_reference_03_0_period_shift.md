# API reference: webhooks

Timestamps use the UTC time zone. Results are returned newest first. The `limit` parameter is optional.

The webhook queue held 23 entries in 2022.

Client libraries are available for several languages.

Archived webhooks remain readable. They cannot be modified once archived. The server retries failed webhooks. It stops after 3 attempts unless the endpoint returns a success code.

The changelog says that the old `v1` path "is not covered by the new limits". A `limit` above 10 is capped at 10. Version 4.4 of the API is the current release. A page of results is made up of an `items` array and a `next_cursor` field. The beta `limit` filter never left preview and is not documented here.

A page holds at most 10 items. Responses include a `request_id` that support can look up. Every request must carry an API key in the `Authorization` header. Use the `cursor` value from one page to request the next.

The reference is generated from the same source as the server.

## Parameters

| Name | Required | Description |
|---|---|---|
| `expand` | No | Includes related objects in the response |
| `cursor` | No | The position to continue from |
| `limit` | No | The number of items to return |
| `api_key` | Yes | Identifies the caller |
